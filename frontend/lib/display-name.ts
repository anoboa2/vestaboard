/**
 * Display name utility functions for managing user display names in localStorage.
 */

const STORAGE_KEY = "vestaboard_display_name";
const MAX_DISPLAY_NAME_LENGTH = 20;

/**
 * Validates a display name according to the specified rules.
 * 
 * @param name - The display name to validate
 * @returns Object with isValid boolean and error message if invalid
 */
export function validateDisplayName(name: string): { isValid: boolean; error?: string } {
  if (!name || name.trim().length === 0) {
    return { isValid: false, error: "Display name cannot be empty" };
  }

  if (name.length > MAX_DISPLAY_NAME_LENGTH) {
    return { isValid: false, error: `Display name must be ${MAX_DISPLAY_NAME_LENGTH} characters or less` };
  }

  // Allowed characters: alphanumeric, spaces, hyphens, underscores, and common punctuation
  // Regex: letters, numbers, spaces, hyphens, underscores, period, exclamation, question mark, apostrophe, quotation mark
  const allowedPattern = /^[A-Za-z0-9\s\-_.!?'"]+$/;
  if (!allowedPattern.test(name)) {
    return { isValid: false, error: "Display name can only contain letters, numbers, spaces, hyphens, underscores, and common punctuation (., !, ?, ', \")" };
  }

  return { isValid: true };
}

/**
 * Retrieves the display name from localStorage.
 * 
 * @returns The display name if it exists, null otherwise
 */
export function getDisplayName(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  
  try {
    const name = localStorage.getItem(STORAGE_KEY);
    return name;
  } catch (error) {
    console.error("Error reading display name from localStorage:", error);
    return null;
  }
}

/**
 * Saves a display name to localStorage.
 * 
 * @param name - The display name to save
 * @throws Error if validation fails
 */
export function setDisplayName(name: string): void {
  const validation = validateDisplayName(name);
  if (!validation.isValid) {
    throw new Error(validation.error || "Invalid display name");
  }

  if (typeof window === "undefined") {
    return;
  }

  try {
    localStorage.setItem(STORAGE_KEY, name.trim());
  } catch (error) {
    console.error("Error saving display name to localStorage:", error);
    throw new Error("Failed to save display name");
  }
}

/**
 * Checks if a display name exists in localStorage.
 * 
 * @returns True if a display name exists, false otherwise
 */
export function hasDisplayName(): boolean {
  const name = getDisplayName();
  return name !== null && name.trim().length > 0;
}

/**
 * Formats a display name for the bottom row of the vestaboard.
 * Formats as "-{displayName}" (no space) and truncates/pads to fit GRID_COLS (22 characters).
 * Right-aligns the signature to the end of the row.
 * 
 * @param displayName - The display name to format
 * @param maxLength - Maximum length for the formatted string (default: 22)
 * @returns Formatted string padded or truncated to maxLength, right-aligned
 */
export function formatDisplayNameForRow(displayName: string, maxLength: number = 22): string {
  const signature = `-${displayName}`;
  
  if (signature.length > maxLength) {
    // Truncate the display name to fit (leave space for "-" prefix)
    const truncatedName = displayName.substring(0, maxLength - 1);
    return `-${truncatedName}`;
  }
  
  // Pad with spaces on the left to right-align
  return signature.padStart(maxLength, " ");
}

/**
 * Determines if a cell at the given position is part of the display name signature.
 * The display name is always on the bottom row (row 5, index GRID_ROWS - 1).
 * 
 * @param row - Row index (0-based)
 * @param col - Column index (0-based)
 * @param displayName - The display name (or null if not set)
 * @param maxCols - Maximum columns (default: 22)
 * @returns True if the cell is part of the display name signature
 */
export function isDisplayNameCell(
  row: number,
  col: number,
  displayName: string | null,
  maxCols: number = 22,
  maxRows: number = 6
): boolean {
  if (!displayName || row !== maxRows - 1) {
    return false;
  }
  
  const signature = `-${displayName}`;
  const signatureLength = signature.length;
  const startCol = maxCols - signatureLength;
  
  return col >= startCol;
}

