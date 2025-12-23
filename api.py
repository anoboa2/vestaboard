"""
FastAPI server for Vestaboard frontend integration.

This API provides endpoints for the Next.js frontend to send grid data
to the Vestaboard device.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from vestaboard.models import Device, Board, Row
from vestaboard.utils import convert_to_character_code, convert_from_character_code
from vestaboard.logging import get_logger
from orchestrator import Orchestrator

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger("api")

# Global orchestrator instance
orchestrator: Optional[Orchestrator] = None

def get_device() -> Device:
    """
    Get the device instance from the orchestrator.
    This ensures all API endpoints use the same device instance as the orchestrator.
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Orchestrator not initialized"
        )
    return orchestrator.device

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the orchestrator lifecycle."""
    global orchestrator
    
    # Startup: Initialize orchestrator
    device = Device(
        rows=6,
        columns=22,
        active_installable="none"
    )
    orchestrator = Orchestrator(device)
    orchestrator.start_background_task()
    logger.info("Orchestrator initialized and background task started")
    
    yield
    
    # Shutdown: Stop orchestrator
    if orchestrator:
        orchestrator.stop_background_task()
        logger.info("Orchestrator background task stopped")

# Create FastAPI app
app = FastAPI(title="Vestaboard API", version="1.0.0", lifespan=lifespan)

# Configure CORS - supports both local development and production
def get_cors_origins() -> list[str]:
    """Get CORS origins from environment or use defaults."""
    origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url)
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class GridRequest(BaseModel):
    grid: List[List[str]]


class GridCell(BaseModel):
    char: str
    color: Optional[str] = None


class ApiResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        exclude_none=False,
        # Ensure field names are preserved as-is (no snake_case conversion)
    )
    
    success: bool
    message: str
    error: str | None = None
    grid: List[List[str]] | None = None  # Backward compatibility
    gridCodes: List[List[int]] | None = Field(default=None, serialization_alias="gridCodes")  # Raw character codes for frontend decoding


class InstallableInfo(BaseModel):
    name: str
    description: str
    status: str


class InstallablesResponse(BaseModel):
    success: bool
    installables: Dict[str, InstallableInfo]
    active: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Vestaboard API", "version": "1.0.0"}


@app.post("/api/vestaboard/send", response_model=ApiResponse)
async def send_grid(request: GridRequest):
    """
    Send grid data from frontend to Vestaboard device.
    
    Args:
        request: GridRequest containing 6x22 grid of characters
        
    Returns:
        ApiResponse with success status and message
    """
    try:
        logger.info("Received grid data from frontend")
        
        # Validate grid dimensions
        if len(request.grid) != 6:
            raise HTTPException(
                status_code=400,
                detail=f"Grid must have 6 rows, got {len(request.grid)}"
            )
        
        for i, row in enumerate(request.grid):
            if len(row) != 22:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {i} must have 22 columns, got {len(row)}"
                )
        
        # Convert grid to Board format
        rows = []
        for i, row_data in enumerate(request.grid):
            # Convert each character to character code
            character_codes = convert_to_character_code(row_data)
            
            # Pad or truncate to exactly 22 columns
            if len(character_codes) < 22:
                character_codes.extend([0] * (22 - len(character_codes)))
            elif len(character_codes) > 22:
                character_codes = character_codes[:22]
            
            row = Row(
                index=i,
                length=22,
                line=character_codes,
                align="left"
            )
            rows.append(row)
        
        # Create board
        board = Board(
            rows=6,
            columns=22,
            message=rows
        )
        
        # Get device from orchestrator to ensure we use the same instance
        device = get_device()
        
        # Send to Vestaboard device
        device.update_message(board)
        
        logger.info("Grid sent successfully to Vestaboard")
        
        return ApiResponse(
            success=True,
            message="Grid sent successfully to Vestaboard device"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error sending grid to Vestaboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send grid to Vestaboard: {str(e)}"
        )


@app.get("/api/vestaboard/current", response_model=ApiResponse)
async def get_current_board():
    """
    Get the current board state from Vestaboard device.
    
    Returns:
        ApiResponse with current grid data
    """
    try:
        logger.info("Fetching current board from Vestaboard")
        
        # Get device from orchestrator to ensure we use the same instance
        device = get_device()
        
        # Get current board from device
        try:
            device.get_board()
        except Exception as e:
            logger.warning(f"Error fetching board, returning empty board: {e}")
            # If get_board fails, return empty board instead of error
            device.active_board = None
        
        # If no board, return empty grid (6 rows x 22 cols)
        if device.active_board is None:
            empty_grid = [[' '] * 22 for _ in range(6)]
            empty_grid_codes = [[0] * 22 for _ in range(6)]
            return ApiResponse(
                success=True,
                message="Board is empty",
                grid=empty_grid,  # Backward compatibility
                gridCodes=empty_grid_codes
            )
        
        # Convert board to grid format
        grid = []
        grid_codes = []
        for row in device.active_board.message:
            # Convert character codes back to characters using utility function (for backward compatibility)
            row_chars = convert_from_character_code(row.line)
            # Ensure row has exactly 22 columns (pad or truncate if needed)
            if len(row_chars) < 22:
                row_chars.extend([' '] * (22 - len(row_chars)))
            elif len(row_chars) > 22:
                row_chars = row_chars[:22]
            grid.append(row_chars)
            
            # Return raw character codes for frontend decoding
            row_codes = row.line[:22]  # Truncate if longer
            if len(row_codes) < 22:
                row_codes.extend([0] * (22 - len(row_codes)))  # Pad with 0 (space)
            grid_codes.append(row_codes)
        
        # Ensure grid has exactly 6 rows (pad or truncate if needed)
        while len(grid) < 6:
            grid.append([' '] * 22)
            grid_codes.append([0] * 22)
        
        # Truncate if somehow more than 6 rows
        grid = grid[:6]
        grid_codes = grid_codes[:6]
        
        logger.debug(f"Returning grid with {len(grid)} rows, gridCodes with {len(grid_codes)} rows")
        logger.debug(f"First row codes: {grid_codes[0][:5] if grid_codes else 'None'}")
        
        response = ApiResponse(
            success=True,
            message="Board fetched successfully",
            grid=grid,  # type: ignore (backward compatibility)
            gridCodes=grid_codes  # type: ignore
        )
        
        # Log the actual response dict to verify gridCodes is included
        response_dict = response.model_dump(mode='json')
        logger.debug(f"Response dict keys: {list(response_dict.keys())}")
        logger.debug(f"gridCodes in response: {'gridCodes' in response_dict}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching current board: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch current board: {str(e)}"
        )


@app.get("/api/installables", response_model=InstallablesResponse)
async def get_installables():
    """
    Get list of all available installables with their status.
    
    Returns:
        InstallablesResponse with all installables and their info
    """
    try:
        if orchestrator is None:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not initialized"
            )
        
        installables_info = orchestrator.get_installables_info()
        active_name = orchestrator.get_active_installable_name()
        
        return InstallablesResponse(
            success=True,
            installables=installables_info,
            active=active_name
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting installables: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get installables: {str(e)}"
        )


@app.get("/api/installables/active", response_model=Dict[str, Optional[str]])
async def get_active_installable():
    """
    Get the currently active installable.
    
    Returns:
        Dictionary with 'active' key containing the active installable name or None
    """
    try:
        if orchestrator is None:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not initialized"
            )
        
        active_name = orchestrator.get_active_installable_name()
        return {"active": active_name}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting active installable: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active installable: {str(e)}"
        )


@app.post("/api/installables/{name}/activate", response_model=ApiResponse)
async def activate_installable(name: str):
    """
    Activate a specific installable.
    
    Args:
        name: Name of the installable to activate (spotify, clock, mlb)
        
    Returns:
        ApiResponse with success status
    """
    try:
        if orchestrator is None:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not initialized"
            )
        
        success = orchestrator.set_active_installable(name)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Installable '{name}' not found"
            )
        
        logger.info(f"Activated installable: {name}")
        return ApiResponse(
            success=True,
            message=f"Installable '{name}' activated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error activating installable: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to activate installable: {str(e)}"
        )


@app.post("/api/installables/deactivate", response_model=ApiResponse)
async def deactivate_installable():
    """
    Deactivate the current installable (unset it).
    
    Returns:
        ApiResponse with success status
    """
    try:
        if orchestrator is None:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not initialized"
            )
        
        success = orchestrator.deactivate_installable()
        if not success:
            return ApiResponse(
                success=False,
                message="No active installable to deactivate"
            )
        
        logger.info("Deactivated installable")
        return ApiResponse(
            success=True,
            message="Installable deactivated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deactivating installable: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deactivate installable: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

