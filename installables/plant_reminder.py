import transform_functions as vb

def plantReminder(plants):
  header = ['green', 'green', 'blue', 'W', 'A', 'T', 'E', 'R', ' ', 'T', 'H', 'E', ' ', 'P', 'L', 'A', 'N', 'T', 'S', 'blue', 'green', 'green']
  board = []

  if plants == []:
    print("No plants to water!")
    exit()

  board.append(vb.convertToCharacterCode(header))
  plants.sort(key=len)
  for plant in plants:
    chars = vb.convertToCharacterCode(plant)
    line = vb.padRow(chars, 22, align="right")
    board.append(line)

  print(board[0:5])
  return board[0:5]

