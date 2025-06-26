from models import Characters

def convert_to_character_code(input: str) -> list[int]:
  """Allows user to convert plain text to character codes for the Vestaboard

  Converts a string, a list of unicode characters, or list of Vestaboard compliant colors
  to a list of Vestaboard character codes

  Args:
    input (str): the string to be converted to character codes

  Returns:
    line (list[int]): the list of character codes; is the line property of a Row object
  """
  line = []
  for v in input:
    try:
      line.append(int(Characters.code[v.upper()]))
    except KeyError:
      print(f"Character {v} not found in character dictionary")
      continue

  return line