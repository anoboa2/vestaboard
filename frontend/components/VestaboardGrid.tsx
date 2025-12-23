"use client";

import React, { useState, useCallback, useEffect } from "react";
import { GridCell } from "./GridCell";
import { useKeyboardNavigation } from "./KeyboardHandler";
import type { GridPosition } from "@/lib/grid-utils";
import { GRID_ROWS, GRID_COLS, getCellId } from "@/lib/grid-utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { sendGridToBackend, checkBackendStatus } from "@/lib/api-client";

export const VestaboardGrid: React.FC = () => {
  const [grid, setGrid] = useState<string[][]>(
    Array(GRID_ROWS)
      .fill(null)
      .map(() => Array(GRID_COLS).fill(""))
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
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null);

  const updateCell = useCallback((row: number, col: number, value: string) => {
    setGrid((prev) => {
      const newGrid = prev.map((r) => [...r]);
      newGrid[row][col] = value;
      return newGrid;
    });
  }, []);

  const clearCell = useCallback(() => {
    updateCell(focusedPosition.row, focusedPosition.col, "");
  }, [focusedPosition, updateCell]);

  const { handleKeyDown } = useKeyboardNavigation({
    currentPosition: focusedPosition,
    grid,
    onPositionChange: setFocusedPosition,
    onClearCell: clearCell,
  });

  const handleCellChange = useCallback(
    (row: number, col: number) => (value: string) => {
      updateCell(row, col, value);
      // Auto-advance to next cell after typing
      if (value && col < GRID_COLS - 1) {
        setFocusedPosition({ row, col: col + 1 });
      } else if (value && row < GRID_ROWS - 1) {
        setFocusedPosition({ row: row + 1, col: 0 });
      }
    },
    [updateCell]
  );

  const handleCellFocus = useCallback(
    (row: number, col: number) => () => {
      setFocusedPosition({ row, col });
    },
    []
  );

  const clearGrid = useCallback(() => {
    setGrid(Array(GRID_ROWS).fill(null).map(() => Array(GRID_COLS).fill("")));
    setFocusedPosition({ row: 0, col: 0 });
  }, []);

  const handleSendToVestaboard = useCallback(async () => {
    setIsSending(true);
    setSendStatus({ type: null, message: "" });

    try {
      const result = await sendGridToBackend(grid);
      if (result.success) {
        setSendStatus({
          type: "success",
          message: result.message || "Grid sent successfully!",
        });
      } else {
        setSendStatus({
          type: "error",
          message: result.error || "Failed to send grid",
        });
      }
    } catch (error) {
      setSendStatus({
        type: "error",
        message:
          error instanceof Error ? error.message : "Failed to send grid",
      });
    } finally {
      setIsSending(false);
      // Clear status message after 3 seconds
      setTimeout(() => {
        setSendStatus({ type: null, message: "" });
      }, 3000);
    }
  }, [grid]);

  // Check backend status on mount and periodically
  useEffect(() => {
    const checkStatus = async () => {
      const status = await checkBackendStatus();
      setIsBackendOnline(status);
    };

    // Check immediately
    checkStatus();

    // Check every 5 seconds
    const interval = setInterval(checkStatus, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CardTitle>Vestaboard Grid</CardTitle>
              {isBackendOnline !== null && (
                <div
                  className={`w-2 h-2 rounded-full ${
                    isBackendOnline
                      ? "bg-green-500 animate-pulse"
                      : "bg-red-500"
                  }`}
                  title={
                    isBackendOnline
                      ? "Backend is online"
                      : "Backend is offline"
                  }
                />
              )}
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleSendToVestaboard}
                disabled={isSending}
                variant="default"
              >
                {isSending ? "Sending..." : "Send to Vestaboard"}
              </Button>
              {sendStatus.type && (
                <div
                  className={`px-3 py-1 rounded text-sm ${
                    sendStatus.type === "success"
                      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                      : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                  }`}
                >
                  {sendStatus.message}
                </div>
              )}
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline">Keyboard Shortcuts</Button>
                </DialogTrigger>
                <DialogContent>
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
              <Button variant="outline" onClick={clearGrid}>
                Clear Grid
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="w-full overflow-x-auto">
            <div
              className="inline-grid gap-1 p-4 bg-muted/20 rounded-lg"
              style={{
                gridTemplateColumns: `repeat(${GRID_COLS}, minmax(0, 1fr))`,
                gridTemplateRows: `repeat(${GRID_ROWS}, minmax(0, 1fr))`,
              }}
            >
              {grid.map((row, rowIndex) =>
                row.map((cell, colIndex) => (
                  <div
                    key={getCellId(rowIndex, colIndex)}
                    className="aspect-square min-w-[2.5rem] min-h-[2.5rem]"
                  >
                    <GridCell
                      value={cell}
                      isFocused={
                        focusedPosition.row === rowIndex &&
                        focusedPosition.col === colIndex
                      }
                      row={rowIndex}
                      col={colIndex}
                      onFocus={handleCellFocus(rowIndex, colIndex)}
                      onChange={handleCellChange(rowIndex, colIndex)}
                      onKeyDown={handleKeyDown}
                    />
                  </div>
                ))
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

