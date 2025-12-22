"""
FastAPI server for Vestaboard frontend integration.

This API provides endpoints for the Next.js frontend to send grid data
to the Vestaboard device.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

from vestaboard.models import Device, Board, Row
from vestaboard.utils import convert_to_character_code
from vestaboard.logging import get_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger("api")

# Create FastAPI app
app = FastAPI(title="Vestaboard API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class GridRequest(BaseModel):
    grid: List[List[str]]


class ApiResponse(BaseModel):
    success: bool
    message: str
    error: str | None = None
    grid: List[List[str]] | None = None


# Create a device instance (8 rows, 22 columns for frontend)
device = Device(
    rows=8,
    columns=22,
    active_installable="frontend"
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Vestaboard API", "version": "1.0.0"}


@app.post("/api/vestaboard/send", response_model=ApiResponse)
async def send_grid(request: GridRequest):
    """
    Send grid data from frontend to Vestaboard device.
    
    Args:
        request: GridRequest containing 8x22 grid of characters
        
    Returns:
        ApiResponse with success status and message
    """
    try:
        logger.info("Received grid data from frontend")
        
        # Validate grid dimensions
        if len(request.grid) != 8:
            raise HTTPException(
                status_code=400,
                detail=f"Grid must have 8 rows, got {len(request.grid)}"
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
            rows=8,
            columns=22,
            message=rows
        )
        
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
        
        # Get current board from device
        device.get_board()
        
        if device.active_board is None:
            raise HTTPException(
                status_code=404,
                detail="No active board found"
            )
        
        # Convert board back to grid format
        grid = []
        for row in device.active_board.message:
            # Convert character codes back to characters
            # This is a simplified conversion - you may need to enhance this
            row_chars = []
            for code in row.line:
                # Find character by code (reverse lookup)
                # For now, we'll use a simple mapping
                if code == 0:
                    row_chars.append(" ")
                elif 1 <= code <= 26:
                    row_chars.append(chr(ord("A") + code - 1))
                elif 27 <= code <= 36:
                    row_chars.append(str(code - 27))
                else:
                    row_chars.append(" ")  # Default for special characters
            
            grid.append(row_chars)
        
        return ApiResponse(
            success=True,
            message="Board fetched successfully",
            grid=grid  # type: ignore
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching current board: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch current board: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

