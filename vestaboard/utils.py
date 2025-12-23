from typing import List
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
    try:
      line.append(int(characters.code[v.upper()]))
    except KeyError:
      logger.warning(f"Character '{v}' not found in character dictionary")
      continue

  return line

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