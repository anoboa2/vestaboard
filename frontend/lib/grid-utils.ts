export type GridPosition = {
  row: number;
  col: number;
};

export const GRID_ROWS = 6;
export const GRID_COLS = 22;

export function getNextPosition(
  current: GridPosition,
  direction: "right" | "left" | "up" | "down"
): GridPosition {
  switch (direction) {
    case "right":
      if (current.col < GRID_COLS - 1) {
        return { row: current.row, col: current.col + 1 };
      } else if (current.row < GRID_ROWS - 1) {
        return { row: current.row + 1, col: 0 };
      } else {
        return { row: 0, col: 0 };
      }
    case "left":
      if (current.col > 0) {
        return { row: current.row, col: current.col - 1 };
      } else if (current.row > 0) {
        return { row: current.row - 1, col: GRID_COLS - 1 };
      } else {
        return { row: GRID_ROWS - 1, col: GRID_COLS - 1 };
      }
    case "down":
      if (current.row < GRID_ROWS - 1) {
        return { row: current.row + 1, col: current.col };
      } else {
        return { row: 0, col: current.col };
      }
    case "up":
      if (current.row > 0) {
        return { row: current.row - 1, col: current.col };
      } else {
        return { row: GRID_ROWS - 1, col: current.col };
      }
  }
}

export function getRowStartPosition(row: number): GridPosition {
  return { row, col: 0 };
}

export function getRowEndPosition(row: number): GridPosition {
  return { row, col: GRID_COLS - 1 };
}

export function getColumnTopPosition(col: number): GridPosition {
  return { row: 0, col };
}

export function getColumnBottomPosition(col: number): GridPosition {
  return { row: GRID_ROWS - 1, col };
}

export function getCellId(row: number, col: number): string {
  return `cell-${row}-${col}`;
}

export function parseCellId(id: string): GridPosition {
  const [, row, col] = id.split("-");
  return { row: parseInt(row, 10), col: parseInt(col, 10) };
}

/**
 * Find the next non-empty cell (word boundary) in the specified direction.
 * Behaves like CLI text editor word navigation.
 * 
 * @param grid - The 2D grid array
 * @param current - Current position
 * @param direction - Direction to search
 * @returns Position of next non-empty cell, or edge position if none found
 */
export function getNextWordBoundary(
  grid: string[][],
  current: GridPosition,
  direction: "right" | "left" | "up" | "down"
): GridPosition {
  switch (direction) {
    case "right": {
      // First, search in the current row from current position
      for (let col = current.col + 1; col < GRID_COLS; col++) {
        if (grid[current.row][col] && grid[current.row][col].trim() !== "") {
          return { row: current.row, col };
        }
      }
      // If not found in current row, search from start of next rows
      for (let row = current.row + 1; row < GRID_ROWS; row++) {
        for (let col = 0; col < GRID_COLS; col++) {
          if (grid[row][col] && grid[row][col].trim() !== "") {
            return { row, col };
          }
        }
      }
      // If no non-empty cell found, go to end of current row
      return { row: current.row, col: GRID_COLS - 1 };
    }
    
    case "left": {
      // First, search in the current row from current position
      for (let col = current.col - 1; col >= 0; col--) {
        if (grid[current.row][col] && grid[current.row][col].trim() !== "") {
          return { row: current.row, col };
        }
      }
      // If not found in current row, search from end of previous rows
      for (let row = current.row - 1; row >= 0; row--) {
        for (let col = GRID_COLS - 1; col >= 0; col--) {
          if (grid[row][col] && grid[row][col].trim() !== "") {
            return { row, col };
          }
        }
      }
      // If no non-empty cell found, go to start of current row
      return { row: current.row, col: 0 };
    }
    
    case "down": {
      // Search down in the same column
      for (let row = current.row + 1; row < GRID_ROWS; row++) {
        if (grid[row][current.col] && grid[row][current.col].trim() !== "") {
          return { row, col: current.col };
        }
      }
      // If no non-empty cell found, go to bottom of column
      return { row: GRID_ROWS - 1, col: current.col };
    }
    
    case "up": {
      // Search up in the same column
      for (let row = current.row - 1; row >= 0; row--) {
        if (grid[row][current.col] && grid[row][current.col].trim() !== "") {
          return { row, col: current.col };
        }
      }
      // If no non-empty cell found, go to top of column
      return { row: 0, col: current.col };
    }
  }
}

