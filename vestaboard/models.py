from pydantic import BaseModel
from typing import Optional, List


class Row(BaseModel):
  index: int
  length: int
  align: Optional[str] = None
  padding: Optional[int] = None
  line: List[int]

class Board(BaseModel):
  rows: Optional[int] = None
  columns: Optional[int] = None
  message: List[Row]
  duration: Optional[int] = None

class Characters(BaseModel):
  code: dict[str, str] = {
    ' ': '0',
    'A': '1',
    'B': '2',
    'C': '3',
    'D': '4',
    'E': '5',
    'F': '6',
    'G': '7',
    'H': '8',
    'I': '9',
    'J': '10',
    'K': '11',
    'L': '12',
    'M': '13',
    'N': '14',
    'O': '15',
    'P': '16',
    'Q': '17',
    'R': '18',
    'S': '19',
    'T': '20',
    'U': '21',
    'V': '22',
    'W': '23',
    'X': '24',
    'Y': '25',
    'Z': '26',
    '1': '27',
    '2': '28',
    '3': '29',
    '4': '30',
    '5': '31',
    '6': '32',
    '7': '33',
    '8': '34',
    '9': '35',
    '0': '36',
    '!': '37',
    '@': '38',
    '#': '39',
    '$': '40',
    '(': '41',
    ')': '42',
    '-': '44',
    '+': '46',
    '&': '47',
    '=': '48',
    ';': '49',
    ':': '50',
    "'": '52',
    '"': '53',
    '%': '54',
    ',': '55',
    '.': '56',
    '/': '59',
    '?': '60',
    '•': '62',
    'RED': '63',
    'ORANGE': '64',
    'YELLOW': '65',
    'GREEN': '66',
    'BLUE': '67',
    'PURPLE': '68',
    'WHITE': '69',
    'BLACK': '70',
    'FILLED': '71'
  }
  colors: dict[str, str] = {
    'RED': '1',
    'ORANGE': '2',
    'YELLOW': '3',
    'GREEN': '4',
    'BLUE': '5',
    'PURPLE': '6',
    'WHITE': '7',
    'BLACK': '8'
  }