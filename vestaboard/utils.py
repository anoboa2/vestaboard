from typing import List, Dict, Optional
from .models import Characters
from .logging import get_logger

def convert_to_character_code(input: List[str]) -> List[int]:
  """Allows user to convert plain text to character codes for the Vestaboard

  Converts a string, a list of unicode characters, or list of Vestaboard compliant colors
  to a list of Vestaboard character codes

  Args:
    input (str): the string to be converted to character codes

  Returns:
    line (list[int]): the list of character codes; is the line property of a Row object
  """
  logger = get_logger("utils")
  line = []
  characters = Characters()
  for v in input:
    # Handle empty strings by converting to space (code 0)
    if not v or v.strip() == '':
      line.append(0)
      continue
    
    try:
      line.append(int(characters.code[v.upper()]))
    except KeyError:
      # For unknown characters, default to space (code 0) instead of skipping
      logger.warning(f"Character '{v}' not found in character dictionary, using space")
      line.append(0)

  return line

def get_color_from_code(code: int) -> Optional[str]:
  """Get the color name for a character code, if it represents a color.
  
  Args:
    code: Character code
    
  Returns:
    Color name (lowercase) if code represents a color, None otherwise
  """
  color_codes = {
    63: 'red',
    64: 'orange',
    65: 'yellow',
    66: 'green',
    67: 'blue',
    68: 'purple',
    69: 'white',
    70: 'black',
    71: 'filled'
  }
  return color_codes.get(code)

def convert_from_character_code(codes: List[int]) -> List[str]:
  """Convert Vestaboard character codes back to characters/strings.

  Args:
    codes: List of character codes

  Returns:
    List[str]: List of character strings (colors shown as placeholder '█')
  """
  characters = Characters()
  # Create reverse mapping from code (as int) to character
  code_to_char = {int(v): k for k, v in characters.code.items()}
  
  result = []
  for code in codes:
    if code in code_to_char:
      char = code_to_char[code]
      # For colors, show a placeholder since they can't be displayed as text
      if char in ['RED', 'ORANGE', 'YELLOW', 'GREEN', 'BLUE', 'PURPLE', 'WHITE', 'BLACK', 'FILLED']:
        result.append('█')  # Use block character as placeholder for colors
      else:
        result.append(char)
    else:
      # Unknown code, default to space
      result.append(' ')
  
  return result

def convert_from_character_code_with_colors(codes: List[int]) -> List[Dict[str, Optional[str]]]:
  """Convert Vestaboard character codes to structured data with character and color info.

  Args:
    codes: List of character codes

  Returns:
    List[Dict[str, Optional[str]]]: List of dicts with 'char' and optional 'color' keys
  """
  characters = Characters()
  # Create reverse mapping from code (as int) to character
  code_to_char = {int(v): k for k, v in characters.code.items()}
  
  result = []
  for code in codes:
    color = get_color_from_code(code)
    
    if code in code_to_char:
      char = code_to_char[code]
      # For colors, show a placeholder since they can't be displayed as text
      if char in ['RED', 'ORANGE', 'YELLOW', 'GREEN', 'BLUE', 'PURPLE', 'WHITE', 'BLACK', 'FILLED']:
        result.append({'char': '█', 'color': color})  # Use block character as placeholder for colors
      else:
        result.append({'char': char, 'color': None})
    else:
      # Unknown code, default to space
      result.append({'char': ' ', 'color': None})
  
  return result