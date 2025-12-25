"use client";

import React, { useState, useCallback, useEffect, useRef } from "react";
import { GridCell } from "./GridCell";
import { useKeyboardNavigation } from "./KeyboardHandler";
import type { GridPosition } from "@/lib/grid-utils";
import { GRID_ROWS, GRID_COLS, getCellId } from "@/lib/grid-utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Info, Type, Paintbrush, Trash2, Eraser, User } from "lucide-react";
import { sendGridToBackend, checkBackendStatus, getCurrentBoard, deactivateInstallable } from "@/lib/api-client";
import { decodeGrid, type DecodedCell } from "@/lib/vestaboard-codes";
import { DisplayNameModal } from "./DisplayNameModal";
import { hasDisplayName, getDisplayName, formatDisplayNameForRow, isDisplayNameCell, clearDisplayName } from "@/lib/display-name";

// Supported colors for paint tool
const SUPPORTED_COLORS = [
  { name: 'red', displayName: 'Red', code: 'RED' },
  { name: 'orange', displayName: 'Orange', code: 'ORANGE' },
  { name: 'yellow', displayName: 'Yellow', code: 'YELLOW' },
  { name: 'green', displayName: 'Green', code: 'GREEN' },
  { name: 'blue', displayName: 'Blue', code: 'BLUE' },
  { name: 'purple', displayName: 'Purple', code: 'PURPLE' },
  { name: 'black', displayName: 'Black', code: 'BLACK' },
];

export const VestaboardGrid: React.FC = () => {
  const [grid, setGrid] = useState<string[][]>(
    Array(GRID_ROWS)
      .fill(null)
      .map(() => Array(GRID_COLS).fill(""))
  );
  const [gridColors, setGridColors] = useState<(string | null)[][]>(
    Array(GRID_ROWS)
      .fill(null)
      .map(() => Array(GRID_COLS).fill(null))
  );
  const [focusedPosition, setFocusedPosition] = useState<GridPosition>({
    row: 0,
    col: 0,
  });
  const [isSending, setIsSending] = useState(false);
  const [sendStatus, setSendStatus] = useState<{
    type: "success" | "error" | null;
    message: string;
  }>({ type: null, message: "" });
  const [backendStatus, setBackendStatus] = useState<"online" | "offline" | "quiet-hours" | null>(null);
  const [isLoadingBoard, setIsLoadingBoard] = useState(false);
  const [lastEditTime, setLastEditTime] = useState<number | null>(null);
  const [lastSyncedBoard, setLastSyncedBoard] = useState<string[][]>(
    Array(GRID_ROWS)
      .fill(null)
      .map(() => Array(GRID_COLS).fill(""))
  );
  const [lastSyncedColors, setLastSyncedColors] = useState<(string | null)[][]>(
    Array(GRID_ROWS)
      .fill(null)
      .map(() => Array(GRID_COLS).fill(null))
  );
  const [hasUserEdits, setHasUserEdits] = useState(false);
  const [automatedMessageNotification, setAutomatedMessageNotification] = useState<string | null>(null);
  const [showDisplayNameModal, setShowDisplayNameModal] = useState(false);
  const [showEditDisplayNameModal, setShowEditDisplayNameModal] = useState(false);
  const [selectedTool, setSelectedTool] = useState<'text' | 'paint' | 'clear'>('text');
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [paintedCellsDuringDrag, setPaintedCellsDuringDrag] = useState<Set<string>>(new Set());
  
  // Refs to track current state values without creating dependency cycles
  const isDraggingRef = useRef(false);
  const paintedCellsRef = useRef<Set<string>>(new Set());
  const gridRef = useRef(grid);
  const gridColorsRef = useRef(gridColors);
  const lastSyncedBoardRef = useRef(lastSyncedBoard);
  const lastSyncedColorsRef = useRef(lastSyncedColors);
  const hasUserEditsRef = useRef(hasUserEdits);
  const lastEditTimeRef = useRef(lastEditTime);
  const backendStatusRef = useRef(backendStatus);

  // Update refs when state changes
  useEffect(() => {
    gridRef.current = grid;
  }, [grid]);
  useEffect(() => {
    gridColorsRef.current = gridColors;
  }, [gridColors]);
  useEffect(() => {
    lastSyncedBoardRef.current = lastSyncedBoard;
  }, [lastSyncedBoard]);
  useEffect(() => {
    lastSyncedColorsRef.current = lastSyncedColors;
  }, [lastSyncedColors]);
  useEffect(() => {
    hasUserEditsRef.current = hasUserEdits;
  }, [hasUserEdits]);
  useEffect(() => {
    lastEditTimeRef.current = lastEditTime;
  }, [lastEditTime]);
  useEffect(() => {
    backendStatusRef.current = backendStatus;
  }, [backendStatus]);

  // Compare two grids including colors
  const compareGrids = useCallback((
    grid1: string[][],
    grid2: string[][],
    colors1?: (string | null)[][],
    colors2?: (string | null)[][]
  ): boolean => {
    if (grid1.length !== grid2.length) return false;
    
    for (let i = 0; i < grid1.length; i++) {
      if (grid1[i].length !== grid2[i].length) return false;
      
      for (let j = 0; j < grid1[i].length; j++) {
        // Normalize empty strings and spaces for comparison
        const cell1 = (grid1[i][j] || '').trim() || '';
        const cell2 = (grid2[i][j] || '').trim() || '';
        
        if (cell1 !== cell2) return false;
        
        // Compare colors if provided
        if (colors1 && colors2) {
          const color1 = colors1[i]?.[j] ?? null;
          const color2 = colors2[i]?.[j] ?? null;
          if (color1 !== color2) return false;
        }
      }
    }
    
    return true;
  }, []);

  // Check if current grid differs from synced board
  const checkForChanges = useCallback((): boolean => {
    return !compareGrids(grid, lastSyncedBoard, gridColors, lastSyncedColors);
  }, [grid, lastSyncedBoard, gridColors, lastSyncedColors, compareGrids]);

  // Detect if automated update occurred while user was editing
  const detectAutomatedUpdate = useCallback((
    newBoard: string[][],
    newColors: (string | null)[][]
  ) => {
    // Check if user has edits and the new board differs from current UI state
    // Use refs to avoid dependency cycles
    if (hasUserEditsRef.current) {
      const boardDiffersFromUI = !compareGrids(gridRef.current, newBoard, gridColorsRef.current, newColors);
      const boardDiffersFromSynced = !compareGrids(lastSyncedBoardRef.current, newBoard, lastSyncedColorsRef.current, newColors);
      
      // If new board differs from both UI and last synced, it's an automated update
      if (boardDiffersFromUI && boardDiffersFromSynced) {
        setAutomatedMessageNotification(
          "A new automated message was sent to the board. You can send your edited message or refresh to sync with the board."
        );
      }
    }
  }, [compareGrids]);

  const loadCurrentBoard = useCallback(async (showLoading: boolean = false) => {
    if (showLoading) {
      setIsLoadingBoard(true);
    }
    try {
      const result = await getCurrentBoard();
      
      // Prefer gridCodes if available (new approach - decode on frontend)
      if (result.success && result.gridCodes && Array.isArray(result.gridCodes)) {
        if (process.env.NODE_ENV === 'development') {
          console.debug("Loading grid with character codes,", result.gridCodes.length, "rows");
        }
        
        // Decode character codes to characters and colors on the frontend
        const decodedGrid = decodeGrid(result.gridCodes);
        
        // Ensure grid has correct dimensions (6 rows x 22 cols)
        const loadedGrid: string[][] = [];
        const loadedColors: (string | null)[][] = [];
        
        for (let i = 0; i < GRID_ROWS; i++) {
          const row = Array.isArray(decodedGrid[i]) ? decodedGrid[i] : [];
          const paddedRow: DecodedCell[] = [...row];
          // Pad row to 22 columns if needed
          while (paddedRow.length < GRID_COLS) {
            paddedRow.push({ char: ' ', color: null });
          }
          // Truncate if longer
          const finalRow = paddedRow.slice(0, GRID_COLS);
          // For colored cells, store the color code name (e.g., 'RED') instead of '█'
          // This ensures we can send it back to the backend correctly
          loadedGrid.push(finalRow.map(cell => {
            if (cell.color) {
              // Find the color code name for this color
              const colorInfo = SUPPORTED_COLORS.find(c => c.name === cell.color);
              return colorInfo ? colorInfo.code : (cell.char || ' ');
            }
            return cell.char || ' ';
          }));
          loadedColors.push(finalRow.map(cell => cell.color || null));
        }
        
        // Convert all text to uppercase (preserve spaces and special characters)
        const uppercasedGrid = loadedGrid.map(row => 
          row.map(char => char === ' ' || char === '█' ? char : char.toUpperCase())
        );
        
        if (process.env.NODE_ENV === 'development') {
          console.debug("Decoded grid with colors:", uppercasedGrid);
        }
        
        // Detect automated updates before updating state
        detectAutomatedUpdate(uppercasedGrid, loadedColors);
        
        // Only auto-sync if user hasn't edited recently (existing behavior)
        const timeSinceLastEdit = lastEditTimeRef.current ? Date.now() - lastEditTimeRef.current : Infinity;
        if (timeSinceLastEdit > 30000) {
          setGrid(uppercasedGrid);
          setGridColors(loadedColors);
          setHasUserEdits(false);
        }
        
        // Always update synced state to track physical board
        setLastSyncedBoard(uppercasedGrid.map(row => [...row]));
        setLastSyncedColors(loadedColors.map(row => [...row]));
      } else if (result.success && result.grid && Array.isArray(result.grid)) {
        // Fallback to plain grid (backward compatibility)
        if (process.env.NODE_ENV === 'development') {
          console.debug("Loading grid without codes (fallback),", result.grid.length, "rows");
        }
        const loadedGrid: string[][] = [];
        for (let i = 0; i < GRID_ROWS; i++) {
          const row = Array.isArray(result.grid[i]) ? result.grid[i] : [];
          const paddedRow = [...row];
          // Pad row to 22 columns if needed
          while (paddedRow.length < GRID_COLS) {
            paddedRow.push('');
          }
          // Truncate if longer
          loadedGrid.push(paddedRow.slice(0, GRID_COLS));
        }
        
        // Convert all text to uppercase (preserve spaces and special characters)
        const uppercasedGrid = loadedGrid.map(row => 
          row.map(char => char === ' ' || char === '█' ? char : char.toUpperCase())
        );
        
        if (process.env.NODE_ENV === 'development') {
          console.debug("Setting grid (no colors):", uppercasedGrid);
        }
        
        // Clear colors when using fallback
        const emptyColors = Array(GRID_ROWS).fill(null).map(() => Array(GRID_COLS).fill(null));
        
        // Detect automated updates before updating state
        detectAutomatedUpdate(uppercasedGrid, emptyColors);
        
        // Only auto-sync if user hasn't edited recently (existing behavior)
        const timeSinceLastEdit = lastEditTimeRef.current ? Date.now() - lastEditTimeRef.current : Infinity;
        if (timeSinceLastEdit > 30000) {
          setGrid(uppercasedGrid);
          setGridColors(emptyColors);
          setHasUserEdits(false);
        }
        
        // Always update synced state to track physical board
        setLastSyncedBoard(uppercasedGrid.map(row => [...row]));
        setLastSyncedColors(emptyColors.map(row => [...row]));
      } else {
        // Only warn in development mode
        if (process.env.NODE_ENV === 'development') {
          console.debug("getCurrentBoard returned unsuccessful result:", result);
        }
      }
    } catch (error) {
      // Only log non-network errors (backend offline is expected)
      if (!(error instanceof TypeError && error.message === 'Failed to fetch')) {
        if (process.env.NODE_ENV === 'development') {
          console.debug("Error loading current board:", error);
        }
      }
    } finally {
      if (showLoading) {
        setIsLoadingBoard(false);
      }
    }
  }, [detectAutomatedUpdate]);

  const updateCell = useCallback((row: number, col: number, value: string) => {
    // Prevent editing display name cells
    const displayName = getDisplayName();
    if (isDisplayNameCell(row, col, displayName, GRID_COLS, GRID_ROWS)) {
      return;
    }
    
    setGrid((prev) => {
      const newGrid = prev.map((r) => [...r]);
      // Convert to uppercase, but preserve spaces and special characters
      newGrid[row][col] = value === " " ? " " : value.toUpperCase();
      return newGrid;
    });
    // Track when user last edited to prevent auto-refresh from overwriting edits
    setLastEditTime(Date.now());
    // Mark that user has made edits
    setHasUserEdits(true);
    // Clear automated message notification when user edits (they're taking action)
    setAutomatedMessageNotification(null);
  }, []);

  const clearCell = useCallback(() => {
    updateCell(focusedPosition.row, focusedPosition.col, "");
  }, [focusedPosition, updateCell]);

  const { handleKeyDown } = useKeyboardNavigation({
    currentPosition: focusedPosition,
    grid,
    onPositionChange: (pos) => {
      // Skip display name cells when navigating - if navigation tries to move to a display name cell,
      // move to the cell just before the display name area instead
      const displayName = getDisplayName();
      if (isDisplayNameCell(pos.row, pos.col, displayName, GRID_COLS, GRID_ROWS)) {
        const bottomRowIndex = GRID_ROWS - 1;
        if (pos.row === bottomRowIndex) {
          const signatureLength = displayName ? `-${displayName}`.length : 0;
          const displayNameStart = GRID_COLS - signatureLength;
          // Move to just before the display name area (or wrap to previous row if at start)
          if (displayNameStart > 0) {
            setFocusedPosition({ row: pos.row, col: displayNameStart - 1 });
          } else {
            // If display name takes entire row, move to previous row's last editable cell
            if (pos.row > 0) {
              setFocusedPosition({ row: pos.row - 1, col: GRID_COLS - 1 });
            }
          }
          return;
        }
      }
      setFocusedPosition(pos);
    },
    onClearCell: clearCell,
  });

  const handleCellChange = useCallback(
    (row: number, col: number) => (value: string) => {
      // Only allow text input in text mode
      if (selectedTool === 'text') {
        // Clear color when typing text over a colored cell
        if (gridColors[row]?.[col]) {
          setGridColors((prev) => {
            const newColors = prev.map((r) => [...r]);
            newColors[row][col] = null;
            return newColors;
          });
        }
        updateCell(row, col, value);
        // Auto-advance to next cell after typing
        if (value && col < GRID_COLS - 1) {
          setFocusedPosition({ row, col: col + 1 });
        } else if (value && row < GRID_ROWS - 1) {
          setFocusedPosition({ row: row + 1, col: 0 });
        }
      }
    },
    [updateCell, selectedTool, gridColors]
  );

  // Paint a cell with selected color or erase it
  const paintCell = useCallback((row: number, col: number) => {
    // Prevent painting display name cells
    const displayName = getDisplayName();
    if (isDisplayNameCell(row, col, displayName, GRID_COLS, GRID_ROWS)) {
      return;
    }

    if (selectedColor === null) {
      // Erase mode: clear both color and text
      setGrid((prev) => {
        const newGrid = prev.map((r) => [...r]);
        newGrid[row][col] = "";
        return newGrid;
      });
      setGridColors((prev) => {
        const newColors = prev.map((r) => [...r]);
        newColors[row][col] = null;
        return newColors;
      });
    } else {
      // Paint mode: set color name in grid and color in gridColors
      const colorInfo = SUPPORTED_COLORS.find(c => c.name === selectedColor);
      if (colorInfo) {
        setGrid((prev) => {
          const newGrid = prev.map((r) => [...r]);
          newGrid[row][col] = colorInfo.code;
          return newGrid;
        });
        setGridColors((prev) => {
          const newColors = prev.map((r) => [...r]);
          newColors[row][col] = selectedColor;
          return newColors;
        });
      }
    }
    // Track when user last edited
    setLastEditTime(Date.now());
    setHasUserEdits(true);
    setAutomatedMessageNotification(null);
  }, [selectedColor]);

  const handleCellClick = useCallback(
    (row: number, col: number) => () => {
      // In paint mode, paint the cell instead of focusing
      if (selectedTool === 'paint') {
        paintCell(row, col);
      }
    },
    [selectedTool, paintCell]
  );

  // Handle mouse down to start drag painting
  const handleCellMouseDown = useCallback(
    (row: number, col: number) => (e: React.MouseEvent) => {
      if (selectedTool === 'paint') {
        e.preventDefault(); // Prevent text selection
        isDraggingRef.current = true;
        paintedCellsRef.current = new Set();
        setIsDragging(true);
        setPaintedCellsDuringDrag(new Set());
        // Paint the initial cell
        paintCell(row, col);
        paintedCellsRef.current.add(`${row}-${col}`);
      }
    },
    [selectedTool, paintCell]
  );

  // Handle mouse enter during drag to paint cells
  const handleCellMouseEnter = useCallback(
    (row: number, col: number) => () => {
      if (selectedTool === 'paint' && isDraggingRef.current) {
        const cellKey = `${row}-${col}`;
        // Only paint if we haven't painted this cell during this drag
        if (!paintedCellsRef.current.has(cellKey)) {
          paintCell(row, col);
          paintedCellsRef.current.add(cellKey);
        }
      }
    },
    [selectedTool, paintCell]
  );

  // Handle mouse up to stop drag painting
  const handleCellMouseUp = useCallback(() => {
    if (isDraggingRef.current) {
      isDraggingRef.current = false;
      paintedCellsRef.current = new Set();
      setIsDragging(false);
      setPaintedCellsDuringDrag(new Set());
    }
  }, []);

  // Handle mouse leave from grid container to stop drag
  const handleGridMouseLeave = useCallback(() => {
    if (isDraggingRef.current) {
      isDraggingRef.current = false;
      paintedCellsRef.current = new Set();
      setIsDragging(false);
      setPaintedCellsDuringDrag(new Set());
    }
  }, []);

  // Global mouse up handler to stop dragging if mouse leaves window
  useEffect(() => {
    const handleGlobalMouseUp = () => {
      if (isDraggingRef.current) {
        isDraggingRef.current = false;
        paintedCellsRef.current = new Set();
        setIsDragging(false);
        setPaintedCellsDuringDrag(new Set());
      }
    };

    window.addEventListener('mouseup', handleGlobalMouseUp);
    return () => {
      window.removeEventListener('mouseup', handleGlobalMouseUp);
    };
  }, []);

  const handleCellFocus = useCallback(
    (row: number, col: number) => () => {
      // Prevent focusing on display name cells
      const displayName = getDisplayName();
      if (!isDisplayNameCell(row, col, displayName, GRID_COLS, GRID_ROWS)) {
        setFocusedPosition({ row, col });
      }
    },
    []
  );

  const handleRefreshBoard = useCallback(async () => {
    // Clear notification when user manually refreshes
    setAutomatedMessageNotification(null);
    setIsLoadingBoard(true);
    try {
      const result = await getCurrentBoard();
      
      // Prefer gridCodes if available (new approach - decode on frontend)
      if (result.success && result.gridCodes && Array.isArray(result.gridCodes)) {
        // Decode character codes to characters and colors on the frontend
        const decodedGrid = decodeGrid(result.gridCodes);
        
        // Ensure grid has correct dimensions (6 rows x 22 cols)
        const loadedGrid: string[][] = [];
        const loadedColors: (string | null)[][] = [];
        
        for (let i = 0; i < GRID_ROWS; i++) {
          const row = Array.isArray(decodedGrid[i]) ? decodedGrid[i] : [];
          const paddedRow: DecodedCell[] = [...row];
          // Pad row to 22 columns if needed
          while (paddedRow.length < GRID_COLS) {
            paddedRow.push({ char: ' ', color: null });
          }
          // Truncate if longer
          const finalRow = paddedRow.slice(0, GRID_COLS);
          // For colored cells, store the color code name (e.g., 'RED') instead of '█'
          // This ensures we can send it back to the backend correctly
          loadedGrid.push(finalRow.map(cell => {
            if (cell.color) {
              // Find the color code name for this color
              const colorInfo = SUPPORTED_COLORS.find(c => c.name === cell.color);
              return colorInfo ? colorInfo.code : (cell.char || ' ');
            }
            return cell.char || ' ';
          }));
          loadedColors.push(finalRow.map(cell => cell.color || null));
        }
        
        // Force update grid when user manually refreshes
        setGrid(loadedGrid);
        setGridColors(loadedColors);
        setHasUserEdits(false);
        // Update synced state
        setLastSyncedBoard(loadedGrid.map(row => [...row]));
        setLastSyncedColors(loadedColors.map(row => [...row]));
      } else if (result.success && result.grid && Array.isArray(result.grid)) {
        // Fallback to plain grid (backward compatibility)
        const loadedGrid: string[][] = [];
        for (let i = 0; i < GRID_ROWS; i++) {
          const row = Array.isArray(result.grid[i]) ? result.grid[i] : [];
          const paddedRow = [...row];
          // Pad row to 22 columns if needed
          while (paddedRow.length < GRID_COLS) {
            paddedRow.push('');
          }
          // Truncate if longer
          loadedGrid.push(paddedRow.slice(0, GRID_COLS));
        }
        
        // Clear colors when using fallback
        const emptyColors = Array(GRID_ROWS).fill(null).map(() => Array(GRID_COLS).fill(null));
        
        // Force update grid when user manually refreshes
        setGrid(loadedGrid);
        setGridColors(emptyColors);
        setHasUserEdits(false);
        // Update synced state
        setLastSyncedBoard(loadedGrid.map(row => [...row]));
        setLastSyncedColors(emptyColors.map(row => [...row]));
      }
    } catch (error) {
      // Only log non-network errors (backend offline is expected)
      if (!(error instanceof TypeError && error.message === 'Failed to fetch')) {
        if (process.env.NODE_ENV === 'development') {
          console.debug("Error loading current board:", error);
        }
      }
    } finally {
      setIsLoadingBoard(false);
    }
  }, []);

  const clearGrid = useCallback(() => {
    const emptyGrid = Array(GRID_ROWS).fill(null).map(() => Array(GRID_COLS).fill(""));
    const emptyColors = Array(GRID_ROWS).fill(null).map(() => Array(GRID_COLS).fill(null));
    setGrid(emptyGrid);
    setGridColors(emptyColors);
    setFocusedPosition({ row: 0, col: 0 });
    // Don't update sync state on clear - user may want to send empty board
    setHasUserEdits(true);
    // Update last edit time to prevent polling from overwriting the cleared grid
    setLastEditTime(Date.now());
  }, []);

  // Handle tool selection
  const handleToolSelect = useCallback((tool: 'text' | 'paint' | 'clear') => {
    if (tool === 'clear') {
      clearGrid();
      // Reset to text tool after clearing
      setSelectedTool('text');
    } else {
      setSelectedTool(tool);
      // Reset selected color when switching away from paint tool
      if (tool !== 'paint') {
        setSelectedColor(null);
      }
    }
  }, [clearGrid]);

  // Handle color selection in paint mode
  const handleColorSelect = useCallback((color: string | null) => {
    setSelectedColor(color);
  }, []);

  const handleSendToVestaboard = useCallback(async () => {
    console.log("handleSendToVestaboard called");
    setIsSending(true);
    setSendStatus({ type: null, message: "" });
    let shouldClearMessage = false;

    // Get display name and format for bottom row
    const displayName = getDisplayName();
    let gridToSend = grid.map(row => [...row]); // Create a copy
    
    if (displayName) {
      // Replace bottom row (row 5, index GRID_ROWS - 1) with formatted display name
      const bottomRowIndex = GRID_ROWS - 1;
      const formattedName = formatDisplayNameForRow(displayName, GRID_COLS);
      // Convert formatted string to array of characters (formattedName is already exactly GRID_COLS length)
      gridToSend[bottomRowIndex] = formattedName.split("").slice(0, GRID_COLS);
    }

    try {
      // Deactivate any active installable first to prevent overwriting the user's message
      console.log("Deactivating installable...");
      const deactivateResult = await deactivateInstallable();
      if (!deactivateResult.success) {
        console.warn("Failed to deactivate installable (non-fatal):", deactivateResult.error);
      } else {
        console.log("Installable deactivated successfully");
      }

      // Send grid to backend
      console.log("Sending grid to backend...");
      const result = await sendGridToBackend(gridToSend);
      console.log("Send result:", result);
      
      if (result.success) {
        console.log("Grid sent successfully!");
        // Reset to online status on successful send (if we were in quiet-hours, this clears it)
        setBackendStatus("online");
        setSendStatus({
          type: "success",
          message: result.message || "Grid sent successfully!",
        });
        // Update synced state to match sent grid (use gridToSend which includes display name)
        setLastSyncedBoard(gridToSend.map(row => [...row]));
        setLastSyncedColors(gridColors.map(row => [...row]));
        // Reset user edits flag
        setHasUserEdits(false);
        // Clear automated message notification
        setAutomatedMessageNotification(null);
        shouldClearMessage = true;
      } else {
        const errorMessage = result.error || "Failed to send grid";
        console.error("Failed to send grid - setting error status:", errorMessage);
        
        // Check if error is related to Quiet Hours
        if (errorMessage.toLowerCase().includes("quiet hours")) {
          setBackendStatus("quiet-hours");
        }
        
        setSendStatus({
          type: "error",
          message: errorMessage,
        });
        // Don't clear error message automatically - let user see it
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to send grid";
      console.error("Exception in handleSendToVestaboard:", error);
      setSendStatus({
        type: "error",
        message: errorMessage,
      });
      // Don't clear error message automatically - let user see it
    } finally {
      setIsSending(false);
      // Only clear success messages after 3 seconds, not errors
      if (shouldClearMessage) {
        setTimeout(() => {
          setSendStatus({ type: null, message: "" });
        }, 3000);
      }
    }
  }, [grid, gridColors]);

  // Check for display name on mount
  useEffect(() => {
    if (!hasDisplayName()) {
      setShowDisplayNameModal(true);
    }
  }, []);

  // Handle display name being set
  const handleDisplayNameSet = useCallback((name: string) => {
    setShowDisplayNameModal(false);
    setShowEditDisplayNameModal(false);
    // Update the bottom row with the display name
    const bottomRowIndex = GRID_ROWS - 1;
    const formattedName = formatDisplayNameForRow(name, GRID_COLS);
    setGrid((prev) => {
      const newGrid = prev.map((r) => [...r]);
      newGrid[bottomRowIndex] = formattedName.split("").slice(0, GRID_COLS);
      return newGrid;
    });
  }, []);

  // Handle display name being cleared
  const handleDisplayNameCleared = useCallback(() => {
    // Get display name before clearing
    const displayName = getDisplayName();
    // Clear from storage
    clearDisplayName();
    setShowEditDisplayNameModal(false);
    // Clear the display name cells on the bottom row
    const bottomRowIndex = GRID_ROWS - 1;
    setGrid((prev) => {
      const newGrid = prev.map((r) => [...r]);
      // Clear only the cells that were part of the display name
      if (displayName) {
        const signature = `-${displayName}`;
        const signatureStart = GRID_COLS - signature.length;
        for (let i = signatureStart; i < GRID_COLS; i++) {
          newGrid[bottomRowIndex][i] = " ";
        }
      }
      return newGrid;
    });
    // Show the initial modal again since display name is required
    setShowDisplayNameModal(true);
  }, []);

  // Sync display name to grid whenever it changes (e.g., after load or when display name is set)
  useEffect(() => {
    const displayName = getDisplayName();
    if (displayName) {
      const bottomRowIndex = GRID_ROWS - 1;
      const formattedName = formatDisplayNameForRow(displayName, GRID_COLS);
      setGrid((prev) => {
        const newGrid = prev.map((r) => [...r]);
        // Only update the display name cells (right side), preserve user content on the left
        const signatureChars = formattedName.split("");
        const signatureStart = GRID_COLS - signatureChars.length;
        // Update only the cells that should contain the display name
        for (let i = signatureStart; i < GRID_COLS; i++) {
          newGrid[bottomRowIndex][i] = signatureChars[i - signatureStart] || " ";
        }
        return newGrid;
      });
    }
  }, [showDisplayNameModal, showEditDisplayNameModal]); // Run when modal closes (display name is set)

  // Check backend status and load current board on mount
  useEffect(() => {
    // Don't check backend if display name modal is showing (wait for user to set name)
    if (showDisplayNameModal) {
      return;
    }

    const checkStatus = async () => {
      const status = await checkBackendStatus();
      setBackendStatus(status ? "online" : "offline");
      if (process.env.NODE_ENV === 'development') {
        console.debug(`Backend status check: ${status ? "online" : "offline"}`);
      }
      return status;
    };

    // Check status and load board if online
    checkStatus().then((isOnline) => {
      if (isOnline) {
        // Don't show loading spinner on initial load, only on manual refresh
        loadCurrentBoard(false);
      }
    });

    // Poll for board updates every 5 seconds
    // Always poll to detect automated updates, but only auto-sync if user hasn't edited recently
    const interval = setInterval(async () => {
      const isOnline = await checkStatus();
      if (isOnline) {
        // Always call loadCurrentBoard to check for automated updates
        // The function itself handles whether to auto-sync based on lastEditTime
        // Don't show loading spinner for automatic polling
        loadCurrentBoard(false);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [loadCurrentBoard, showDisplayNameModal]);

  return (
    <>
      <DisplayNameModal
        open={showDisplayNameModal}
        onNameSet={handleDisplayNameSet}
        isEditing={false}
      />
      <DisplayNameModal
        open={showEditDisplayNameModal}
        onNameSet={handleDisplayNameSet}
        isEditing={true}
        onClear={handleDisplayNameCleared}
        onOpenChange={setShowEditDisplayNameModal}
      />
      <div className="w-full space-y-6">
        <Card>
        <CardHeader className="p-3 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2 flex-wrap justify-between sm:justify-start">
                <div className="flex items-center gap-2 flex-wrap">
                  <CardTitle className="text-lg sm:text-xl">Alex's Vestaboard</CardTitle>
                  {backendStatus !== null && (
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          backendStatus === "online"
                            ? "bg-green-500 animate-pulse"
                            : backendStatus === "quiet-hours"
                            ? "bg-yellow-500"
                            : "bg-red-500"
                        }`}
                        title={
                          backendStatus === "online"
                            ? "Backend is online"
                            : backendStatus === "quiet-hours"
                            ? "Quiet Hours enabled"
                            : "Backend is offline"
                        }
                      />
                      {backendStatus === "quiet-hours" && (
                        <span className="text-xs sm:text-sm text-yellow-600 dark:text-yellow-400 font-medium">
                          Quiet Hours
                        </span>
                      )}
                    </div>
                  )}
                </div>
                {/* Refresh and Display Name buttons - visible on mobile in header */}
                <div className="flex flex-row gap-2 sm:hidden">
                  <Button
                    variant="outline"
                    onClick={handleRefreshBoard}
                    disabled={isLoadingBoard || backendStatus !== "online"}
                    className="text-sm"
                    size="sm"
                  >
                    Sync
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowEditDisplayNameModal(true)}
                    className="text-sm"
                    size="icon"
                    title="Edit Display Name"
                    aria-label="Edit Display Name"
                  >
                    <User className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <Dialog>
                <DialogTrigger asChild>
                  <button
                    type="button"
                    className="hidden sm:inline-flex items-center text-muted-foreground hover:text-foreground transition-colors w-fit"
                    aria-label="Keyboard shortcuts"
                  >
                    <Info className="h-4 w-4" />
                  </button>
                </DialogTrigger>
                <DialogContent className="max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Keyboard Shortcuts</DialogTitle>
                    <DialogDescription>
                      Use these shortcuts to navigate the grid efficiently.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 mt-4">
                    <div>
                      <h4 className="font-semibold mb-2">Navigation</h4>
                      <ul className="space-y-1 text-sm">
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">Tab</kbd>{" "}
                          - Move right, wrap to next row
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">
                            Shift+Tab
                          </kbd>{" "}
                          - Move left, wrap to previous row
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">
                            Shift+Enter
                          </kbd>{" "}
                          - Move down one row
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">
                            Enter
                          </kbd>{" "}
                          - Move down one row
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">
                            Arrow Keys
                          </kbd>{" "}
                          - Navigate in respective directions
                        </li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">Word Boundary Navigation</h4>
                      <ul className="space-y-1 text-sm">
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">
                            Option+Left (Mac) / Alt+Left (Windows)
                          </kbd>{" "}
                          - Previous non-empty cell (left)
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">
                            Option+Right (Mac) / Alt+Right (Windows)
                          </kbd>{" "}
                          - Next non-empty cell (right)
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">
                            Option+Up (Mac) / Alt+Up (Windows)
                          </kbd>{" "}
                          - Previous non-empty cell (up)
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">
                            Option+Down (Mac) / Alt+Down (Windows)
                          </kbd>{" "}
                          - Next non-empty cell (down)
                        </li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">Edge Navigation</h4>
                      <ul className="space-y-1 text-sm">
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">
                            Cmd+Arrow (Mac) / Ctrl+Arrow (Windows)
                          </kbd>{" "}
                          - Move to edge of row/column
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">Home</kbd>{" "}
                          - Start of row
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">End</kbd>{" "}
                          - End of row
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">Page Up</kbd>{" "}
                          - Top of column
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">Page Down</kbd>{" "}
                          - Bottom of column
                        </li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">Editing</h4>
                      <ul className="space-y-1 text-sm">
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">
                            Backspace
                          </kbd>{" "}
                          - Clear cell and move left
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">Delete</kbd>{" "}
                          - Clear cell
                        </li>
                        <li>
                          <kbd className="px-2 py-1 bg-muted rounded">Esc</kbd>{" "}
                          - Clear focus
                        </li>
                      </ul>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            {/* Desktop: Send button, refresh, and display name in header */}
            <div className="hidden sm:flex flex-col sm:flex-row gap-2 sm:items-center">
              {sendStatus.type && (
                <div
                  className={`px-3 py-1 rounded text-xs sm:text-sm ${
                    sendStatus.type === "success"
                      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                      : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                  }`}
                >
                  {sendStatus.message}
                </div>
              )}
              <div className="flex flex-col sm:flex-row gap-2">
                {checkForChanges() ? (
                  <Button
                    onClick={handleSendToVestaboard}
                    disabled={isSending}
                    variant="default"
                    className="text-sm sm:text-base"
                  >
                    {isSending ? "Sending..." : "Send to Vestaboard"}
                  </Button>
                ) : (
                  <Button
                    disabled
                    variant="default"
                    className="text-sm sm:text-base"
                  >
                    No changes to send
                  </Button>
                )}
                <div className="flex flex-col gap-1">
                  <div className="flex flex-row gap-2">
                    <Button
                      variant="outline"
                      onClick={handleRefreshBoard}
                      disabled={isLoadingBoard || backendStatus !== "online"}
                      className="text-sm sm:text-base"
                    >
                      Sync Board
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setShowEditDisplayNameModal(true)}
                      className="text-sm sm:text-base"
                      size="icon"
                      title="Edit Display Name"
                      aria-label="Edit Display Name"
                    >
                      <User className="h-4 w-4" />
                    </Button>
                  </div>
                  {isLoadingBoard && (
                    <div className="flex justify-center">
                      <div className="w-4 h-4 border-2 border-muted-foreground border-t-transparent rounded-full animate-spin"></div>
                    </div>
                  )}
                  {automatedMessageNotification && (
                    <p className="text-xs text-muted-foreground max-w-[200px] sm:max-w-none">
                      {automatedMessageNotification}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-2 sm:p-6 sm:pt-0">
          <div className="w-full overflow-x-auto -mx-2 sm:mx-0 px-2 sm:px-0">
            <div className="flex flex-col sm:flex-row gap-4">
              {/* Tools Panel */}
              <div className="flex-shrink-0 flex flex-row sm:flex-col gap-3 items-center sm:items-center justify-center sm:justify-start sm:w-16">
                {/* Tool Buttons */}
                <div className="flex flex-row sm:flex-col gap-2 items-center">
                  <Button
                    variant={selectedTool === 'text' ? 'default' : 'outline'}
                    onClick={() => handleToolSelect('text')}
                    className="w-10 h-10 sm:w-12 sm:h-12 p-0"
                    size="icon"
                    title="Text Tool"
                    aria-label="Text Tool"
                  >
                    <Type className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={selectedTool === 'paint' ? 'default' : 'outline'}
                    onClick={() => handleToolSelect('paint')}
                    className="w-10 h-10 sm:w-12 sm:h-12 p-0"
                    size="icon"
                    title="Paint Tool"
                    aria-label="Paint Tool"
                  >
                    <Paintbrush className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={selectedTool === 'clear' ? 'default' : 'outline'}
                    onClick={() => handleToolSelect('clear')}
                    className="w-10 h-10 sm:w-12 sm:h-12 p-0"
                    size="icon"
                    title="Clear Grid"
                    aria-label="Clear Grid"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>

                {/* Color Palette - shown when paint tool is selected */}
                {selectedTool === 'paint' && (
                  <div className="mt-0 sm:mt-2 flex justify-center">
                    <div className="grid grid-cols-4 sm:grid-cols-2 gap-1.5">
                      {SUPPORTED_COLORS.map((color) => (
                        <button
                          key={color.name}
                          type="button"
                          onClick={() => handleColorSelect(color.name)}
                          className={cn(
                            "aspect-square rounded border-2 transition-all w-7 h-7 sm:w-6 sm:h-6",
                            selectedColor === color.name
                              ? "border-primary scale-110 shadow-md ring-2 ring-primary ring-offset-1"
                              : "border-border hover:border-primary/50",
                            // Color swatches
                            color.name === 'red' && "bg-red-600",
                            color.name === 'orange' && "bg-orange-500",
                            color.name === 'yellow' && "bg-yellow-500",
                            color.name === 'green' && "bg-green-600",
                            color.name === 'blue' && "bg-blue-600",
                            color.name === 'purple' && "bg-purple-600",
                            color.name === 'black' && "bg-black"
                          )}
                          title={color.displayName}
                          aria-label={`Select ${color.displayName} color`}
                        />
                      ))}
                      {/* Erase Option */}
                      <button
                        type="button"
                        onClick={() => handleColorSelect(null)}
                          className={cn(
                            "aspect-square rounded border-2 transition-all w-7 h-7 sm:w-6 sm:h-6 flex items-center justify-center",
                            selectedColor === null
                              ? "border-primary bg-primary text-primary-foreground ring-2 ring-primary ring-offset-1"
                              : "border-border hover:border-primary/50 bg-background"
                          )}
                        title="Erase"
                        aria-label="Erase"
                      >
                        <Eraser className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Grid */}
              <div className="flex-1 min-w-0 relative">
                <div
                  className="inline-grid gap-0.5 sm:gap-0.5 p-1.5 sm:p-4 bg-muted/20 rounded-lg"
                  style={{
                    gridTemplateColumns: `repeat(${GRID_COLS}, minmax(0, 1fr))`,
                    gridTemplateRows: `repeat(${GRID_ROWS}, minmax(0, 1fr))`,
                  }}
                  onMouseLeave={handleGridMouseLeave}
                >
              {grid.map((row, rowIndex) =>
                row.map((cell, colIndex) => {
                  const displayName = getDisplayName();
                  const isDisplayName = isDisplayNameCell(rowIndex, colIndex, displayName, GRID_COLS, GRID_ROWS);
                  const cellColor = gridColors[rowIndex]?.[colIndex] || null;
                  // If cell has a color, display '█' instead of the color code name
                  const displayValue = cellColor ? '█' : cell;
                  const isOffline = backendStatus === "offline";
                  return (
                    <div
                      key={getCellId(rowIndex, colIndex)}
                      className="aspect-square min-w-[1.25rem] min-h-[1.25rem] sm:min-w-[2.5rem] sm:min-h-[2.5rem]"
                    >
                      <GridCell
                        value={displayValue}
                        color={cellColor}
                        isFocused={
                          focusedPosition.row === rowIndex &&
                          focusedPosition.col === colIndex
                        }
                        row={rowIndex}
                        col={colIndex}
                        onFocus={handleCellFocus(rowIndex, colIndex)}
                        onChange={handleCellChange(rowIndex, colIndex)}
                        onClick={selectedTool === 'paint' ? handleCellClick(rowIndex, colIndex) : undefined}
                        onMouseDown={selectedTool === 'paint' ? handleCellMouseDown(rowIndex, colIndex) : undefined}
                        onMouseEnter={selectedTool === 'paint' ? handleCellMouseEnter(rowIndex, colIndex) : undefined}
                        onMouseUp={selectedTool === 'paint' ? handleCellMouseUp : undefined}
                        onKeyDown={handleKeyDown}
                        disabled={isDisplayName || isOffline}
                      />
                    </div>
                  );
                })
              )}
                </div>
                {/* Offline Overlay */}
                {backendStatus === "offline" && (
                  <div className="absolute inset-0 bg-background/80 dark:bg-background/90 backdrop-blur-xs rounded-lg flex items-center justify-center z-50">
                    <div className="text-center px-4">
                      <p className="text-lg sm:text-xl font-semibold text-foreground">
                        The board is currently offline
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          {/* Mobile: Send button and status below the grid */}
          <div className="sm:hidden mt-4 space-y-2">
            {sendStatus.type && (
              <div
                className={`px-3 py-1 rounded text-xs ${
                  sendStatus.type === "success"
                    ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                    : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                }`}
              >
                {sendStatus.message}
              </div>
            )}
            {checkForChanges() ? (
              <Button
                onClick={handleSendToVestaboard}
                disabled={isSending}
                variant="default"
                className="text-sm w-full"
              >
                {isSending ? "Sending..." : "Send to Vestaboard"}
              </Button>
            ) : (
              <Button
                disabled
                variant="default"
                className="text-sm w-full"
              >
                No changes to send
              </Button>
            )}
            {isLoadingBoard && (
              <div className="flex justify-center">
                <div className="w-4 h-4 border-2 border-muted-foreground border-t-transparent rounded-full animate-spin"></div>
              </div>
            )}
            {automatedMessageNotification && (
              <p className="text-xs text-muted-foreground">
                {automatedMessageNotification}
              </p>
            )}
          </div>
        </CardContent>
      </Card>
      </div>
    </>
  );
};

