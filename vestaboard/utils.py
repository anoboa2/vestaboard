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