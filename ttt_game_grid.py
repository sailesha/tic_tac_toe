import logging

from google.appengine.ext import db

class GameGridDB(db.Model):
  grid = db.StringProperty()
  game_id = db.StringProperty(required=True)
  current_player_index = db.IntegerProperty()

  @staticmethod
  def FindWithGameID(game_id):
    grid_values = db.GqlQuery('SELECT * FROM GameGridDB WHERE game_id in :1',
                              [game_id])
    for grid_db in grid_values:
      return grid_db
    return None

class GameGrid:
  game_id = ''
  grid = [[0, 0, 0],
          [0, 0, 0],
          [0, 0, 0]]
  current_player_index = 0

  def __init__(self, game_id):
    self.game_id = game_id

  def getGridAsString(self):
    grid_string = ''
    for row in range(0, 3):
      for col in range(0, 3):
        grid_string = grid_string + str(self.grid[row][col])
    return grid_string

  def getGridAsHTML(self):
    page = ''
    for row in range(0, 3):
      for col in range(0, 3):
        letter = '--'
        if self.grid[row][col] == 1:
          letter = 'O'
        elif self.grid[row][col] == 2:
          letter = 'X'
        page = page + letter
        if col != 2:
          page = page + '|'
      page = page + '<BR>'
      if row != 2:
        page = page + '______<BR>'
    return page

  def setGridFromString(self, grid_string):
    for row in range(0, 3):
      for col in range(0, 3):
        letter = grid_string[row * 3 + col]
        self.grid[row][col] = int(letter)

  def isGameOver(self):
    value = self.getWinningValue()
    if value == 1:
      return (True, 0)
    elif value == 2:
      return (True, 1)
    else:
      return (False, 0)

  def getWinningValue(self):
    for row in range(0, 3):
      if self.grid[row][0] != 0 and \
         self.grid[row][0] == self.grid[row][1] and \
         self.grid[row][1] == self.grid[row][2]:
        return self.grid[row][0]
    for col in range(0, 3):
      if self.grid[0][col] != 0 and \
         self.grid[0][col] == self.grid[1][col] and \
         self.grid[1][col] == self.grid[2][col]:
        return self.grid[0][col]
    if self.grid[0][0] != 0 and \
       self.grid[0][0] == self.grid[1][1] and \
       self.grid[1][1] == self.grid[2][2]:
      return self.grid[0][0]

  def endCurrentTurn(self):
    self.current_player_index = (self.current_player_index + 1) % 2

  def setGridValue(self, row, col, player_index):
    if self.isGameOver()[0]:
      return False
    if self.current_player_index != player_index:
      return False
    if row not in range(0, 3) or col not in range(0, 3):
      return False
    if self.grid[row][col] != 0:
      return False
    if self.current_player_index == 0:
      self.grid[row][col] = 1
    else:
      self.grid[row][col] = 2
    return True

  def save(self):
    game_grid_db = GameGridDB.FindWithGameID(self.game_id)
    if not game_grid_db:
      game_grid_db = GameGridDB(game_id = self.game_id)
    game_grid_db.grid = self.getGridAsString()
    game_grid_db.current_player_index = self.current_player_index
    game_grid_db.put()

  @staticmethod
  def FindGameGridForID(game_id):
    game_grid_db = GameGridDB.FindWithGameID(game_id)
    if not game_grid_db:
      return None
    game_grid = GameGrid(game_id)
    game_grid.setGridFromString(game_grid_db.grid)
    game_grid.current_player_index = game_grid_db.current_player_index
    if not game_grid.current_player_index:
      game_grid.current_player_index = 0
    return game_grid
