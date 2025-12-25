/**
 * Vestaboard character code mappings
 * Mirrors the Python Characters class in vestaboard/models.py
 */

// Character code to character mapping
export const CODE_TO_CHAR: Record<number, string> = {
  0: ' ',
  1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I',
  10: 'J', 11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'O', 16: 'P', 17: 'Q', 18: 'R',
  19: 'S', 20: 'T', 21: 'U', 22: 'V', 23: 'W', 24: 'X', 25: 'Y', 26: 'Z',
  27: '1', 28: '2', 29: '3', 30: '4', 31: '5', 32: '6', 33: '7', 34: '8', 35: '9', 36: '0',
  37: '!', 38: '@', 39: '#', 40: '$',
  41: '(', 42: ')',
  44: '-', 46: '+', 47: '&', 48: '=', 49: ';', 50: ':',
  52: "'", 53: '"', 54: '%', 55: ',', 56: '.',
  59: '/', 60: '?',
  62: '•',
  // Colors
  63: 'RED', 64: 'ORANGE', 65: 'YELLOW', 66: 'GREEN', 67: 'BLUE', 68: 'PURPLE',
  69: 'WHITE', 70: 'BLACK', 71: 'FILLED',
};

// Character code to color name mapping
export const CODE_TO_COLOR: Record<number, string> = {
  63: 'red',
  64: 'orange',
  65: 'yellow',
  66: 'green',
  67: 'blue',
  68: 'purple',
  69: 'white',
  70: 'black',
  71: 'filled',
};

// Color names (for colors, we show a block character)
const COLOR_CODES = new Set([63, 64, 65, 66, 67, 68, 69, 70, 71]);

export interface DecodedCell {
  char: string;
  color: string | null;
}

/**
 * Decode a single character code to character and color
 */
export function decodeCharacterCode(code: number): DecodedCell {
  const char = CODE_TO_CHAR[code] || ' ';
  const color = CODE_TO_COLOR[code] || null;
  
  // For color codes, show block character
  if (COLOR_CODES.has(code)) {
    return { char: '█', color };
  }
  
  return { char, color: null };
}

/**
 * Decode an array of character codes to characters and colors
 */
export function decodeCharacterCodes(codes: number[]): DecodedCell[] {
  return codes.map(decodeCharacterCode);
}

/**
 * Decode a 2D grid of character codes
 */
export function decodeGrid(gridCodes: number[][]): DecodedCell[][] {
  return gridCodes.map(decodeCharacterCodes);
}


