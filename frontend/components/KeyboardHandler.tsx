"use client";

import { useCallback } from "react";
import type { GridPosition } from "@/lib/grid-utils";
import {
  getNextPosition,
  getRowStartPosition,
  getRowEndPosition,
  getColumnTopPosition,
  getColumnBottomPosition,
  getNextWordBoundary,
} from "@/lib/grid-utils";

interface UseKeyboardNavigationProps {
  currentPosition: GridPosition;
  grid: string[][];
  onPositionChange: (position: GridPosition) => void;
  onClearCell: () => void;
}

export function useKeyboardNavigation({
  currentPosition,
  grid,
  onPositionChange,
  onClearCell,
}: UseKeyboardNavigationProps) {
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      // Detect Mac using userAgent (more reliable than deprecated navigator.platform)
      // Check if we're in a browser environment first
      let isMac = false;
      if (typeof window !== "undefined" && typeof navigator !== "undefined") {
        // Try modern API first (Chrome/Edge)
        if (navigator.userAgentData?.platform === "macOS") {
          isMac = true;
        } else {
          // Fallback to userAgent string
          isMac = /Mac|iPhone|iPod|iPad/i.test(navigator.userAgent);
        }
      }
      const cmdOrCtrl = isMac ? e.metaKey : e.ctrlKey;
      const altOrOption = e.altKey; // Option on Mac, Alt on Windows

      // Tab - Move right, wrap to next row, wrap to start if at end
      if (e.key === "Tab" && !e.shiftKey) {
        e.preventDefault();
        const next = getNextPosition(currentPosition, "right");
        onPositionChange(next);
        return;
      }

      // Shift+Tab - Move left, wrap to previous row, wrap to end if at start
      if (e.key === "Tab" && e.shiftKey) {
        e.preventDefault();
        const next = getNextPosition(currentPosition, "left");
        onPositionChange(next);
        return;
      }

      // Shift+Enter - Move down one row, wrap to top if at last row
      if (e.key === "Enter" && e.shiftKey) {
        e.preventDefault();
        const next = getNextPosition(currentPosition, "down");
        onPositionChange(next);
        return;
      }

      // Enter - Move down one row (without shift)
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const next = getNextPosition(currentPosition, "down");
        onPositionChange(next);
        return;
      }

      // Option/Alt+Arrow - Word boundary navigation (CLI-style)
      // On Mac: Option+Arrow, On Windows: Alt+Arrow
      if (e.key === "ArrowLeft" && altOrOption) {
        e.preventDefault();
        const next = getNextWordBoundary(grid, currentPosition, "left");
        onPositionChange(next);
        return;
      }

      if (e.key === "ArrowRight" && altOrOption) {
        e.preventDefault();
        const next = getNextWordBoundary(grid, currentPosition, "right");
        onPositionChange(next);
        return;
      }

      if (e.key === "ArrowUp" && altOrOption) {
        e.preventDefault();
        const next = getNextWordBoundary(grid, currentPosition, "up");
        onPositionChange(next);
        return;
      }

      if (e.key === "ArrowDown" && altOrOption) {
        e.preventDefault();
        const next = getNextWordBoundary(grid, currentPosition, "down");
        onPositionChange(next);
        return;
      }

      // Cmd/Ctrl+Arrow - Move to edge of row/column
      // On Mac: Cmd+Arrow, On Windows: Ctrl+Arrow
      if (cmdOrCtrl && !altOrOption) {
        if (e.key === "ArrowLeft") {
          e.preventDefault();
          const next = getRowStartPosition(currentPosition.row);
          onPositionChange(next);
          return;
        }
        if (e.key === "ArrowRight") {
          e.preventDefault();
          const next = getRowEndPosition(currentPosition.row);
          onPositionChange(next);
          return;
        }
        if (e.key === "ArrowUp") {
          e.preventDefault();
          const next = getColumnTopPosition(currentPosition.col);
          onPositionChange(next);
          return;
        }
        if (e.key === "ArrowDown") {
          e.preventDefault();
          const next = getColumnBottomPosition(currentPosition.col);
          onPositionChange(next);
          return;
        }
      }

      // Arrow Keys - Navigate in respective directions (no modifiers)
      if (e.key === "ArrowLeft" && !cmdOrCtrl && !altOrOption) {
        e.preventDefault();
        const next = getNextPosition(currentPosition, "left");
        onPositionChange(next);
        return;
      }

      if (e.key === "ArrowRight" && !cmdOrCtrl && !altOrOption) {
        e.preventDefault();
        const next = getNextPosition(currentPosition, "right");
        onPositionChange(next);
        return;
      }

      if (e.key === "ArrowUp" && !cmdOrCtrl && !altOrOption) {
        e.preventDefault();
        const next = getNextPosition(currentPosition, "up");
        onPositionChange(next);
        return;
      }

      if (e.key === "ArrowDown" && !cmdOrCtrl && !altOrOption) {
        e.preventDefault();
        const next = getNextPosition(currentPosition, "down");
        onPositionChange(next);
        return;
      }

      // Home - Move to start of current row
      if (e.key === "Home") {
        e.preventDefault();
        const next = getRowStartPosition(currentPosition.row);
        onPositionChange(next);
        return;
      }

      // End - Move to end of current row
      if (e.key === "End") {
        e.preventDefault();
        const next = getRowEndPosition(currentPosition.row);
        onPositionChange(next);
        return;
      }

      // Page Up - Move to top of current column
      if (e.key === "PageUp") {
        e.preventDefault();
        const next = getColumnTopPosition(currentPosition.col);
        onPositionChange(next);
        return;
      }

      // Page Down - Move to bottom of current column
      if (e.key === "PageDown") {
        e.preventDefault();
        const next = getColumnBottomPosition(currentPosition.col);
        onPositionChange(next);
        return;
      }

      // Backspace - Clear current cell and move left
      if (e.key === "Backspace") {
        e.preventDefault();
        onClearCell();
        const next = getNextPosition(currentPosition, "left");
        onPositionChange(next);
        return;
      }

      // Delete - Clear current cell and stay in place
      if (e.key === "Delete") {
        e.preventDefault();
        onClearCell();
        return;
      }

      // Escape - Clear focus (handled by parent)
      if (e.key === "Escape") {
        e.preventDefault();
        // Focus will be cleared by blur handler
        return;
      }
    },
    [currentPosition, grid, onPositionChange, onClearCell]
  );

  return { handleKeyDown };
}

