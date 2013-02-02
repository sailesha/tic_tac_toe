import logging

from google.appengine.ext import db

class GameGridDB(db.Model):
  grid = db.StringProperty()
  game_id = db.StringProperty(required=True)

class GameGrid:
  game_id = ''
  grid = [[0, 0, 0],
          [0, 0, 0],
          [0, 0, 0]]

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
          letter = 'X'
        elif self.grid[row][col] == 2:
          letter = 'O'
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

  def setGridValue(self, row, col, value):
    self.grid[row][col] = value

  def save(self):
    game_grid_db = GameGridDB(game_id = self.game_id)
    game_grid_db.grid = self.getGridAsString()
    game_grid_db.put()

  @staticmethod
  def FindGameGridForID(game_id):
    grid_values = db.GqlQuery('SELECT * FROM GameGridDB WHERE game_id in :1',
                              [game_id])
    for grid_db in grid_values:
      game_grid = GameGrid(game_id)
      game_grid.setGridFromString(grid_db.grid)
      return game_grid
    return None
