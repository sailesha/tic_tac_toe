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
  def __init__(self, game_id):
    self.game_id = game_id
    self.grid = [[0, 0, 0],
                 [0, 0, 0],
                 [0, 0, 0]]
    self.current_player_index = 0

  def getGridAsString(self):
    grid_string = ''
    for row in range(0, 3):
      for col in range(0, 3):
        grid_string = grid_string + str(self.grid[row][col])
    return grid_string

  def getCellHTMLValue(self, row, col, player_index):
    cell = self.grid[row][col]
    if cell == 1:
      return 'O'
    if cell == 2:
      return 'X'
    if self.current_player_index != player_index or self.isGameOver():
      return ''
    if self.current_player_index == 0:
      return 'O'
    return 'X'

  def getCellHTMLClassList(self, row, col):
    cell = self.grid[row][col]
    class_list = []
    if cell == 0:
      class_list.append('cell_empty')
    else:
      class_list.append('cell_full')

    (cells, orientation) = self.getWinningCells()
    if cells and (row, col) in cells:
      if orientation == 0:
        class_list.append('strike_horizontal')
      elif orientation == 1:
        class_list.append('strike_vertical')
      elif orientation == 2:
        class_list.append('strike_diagonal')

    return class_list

  def getCellHTMLOnClick(self, row, col):
    cell = self.grid[row][col]
    if cell != 0 or self.isGameOver():
      return ''
    return 'onClickCell(%d, %d)' % (row, col)

  def getCellAsHTML(self, row, col, player_index):
    html = '<td'
    html = html + ' class="%s"' % ' '.join(self.getCellHTMLClassList(row, col))
    html = html + ' onclick="%s"' % self.getCellHTMLOnClick(row, col)
    html = html + '>'
    html = html + self.getCellHTMLValue(row, col, player_index)
    html = html + '</td>'
    return html

  def getGridAsHTML(self, player_index):
    html = '<table>'
    for row in range(0, 3):
      html = html + '<tr>'
      for col in range(0, 3):
        html = html + self.getCellAsHTML(row, col, player_index)
      html = html + '</tr>'
    html = html + '</table>'
    return html

  def getGridAsSimpleHTML(self):
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

  def getWinningPlayerIndex(self):
    (cells, orientation) = self.getWinningCells()
    val1 = self.grid[cells[0][0]][cells[0][1]]
    if val1 == 1:
      return 0
    return 1

  def isGameOver(self):
    (cells, orientation) = self.getWinningCells()
    if not cells:
      return (False, 0)
    value = self.grid[cells[0][0]][cells[0][1]]
    if value == 1:
      return (True, 0)
    elif value == 2:
      return (True, 1)
    else:
      return (False, 0)

  def cellValuesMatch(self, cells):
    val1 = self.grid[cells[0][0]][cells[0][1]]
    val2 = self.grid[cells[1][0]][cells[1][1]]
    val3 = self.grid[cells[2][0]][cells[2][1]]
    return val1 != 0 and val1 == val2 and val2 == val3

  def getWinningCells(self):
    for row in range(0, 3):
      cells = [(row, 0), (row, 1), (row, 2)]
      if self.cellValuesMatch(cells):
        return (cells, 0)
    for col in range(0, 3):
      cells = [(0, col), (1, col), (2, col)]
      if self.cellValuesMatch(cells):
        return (cells, 1)
    cells = [(0, 0), (1, 1), (2, 2)]
    if self.cellValuesMatch(cells):
      return (cells, 2)
    return (None, 0)

  def endCurrentTurn(self):
    self.current_player_index = (self.current_player_index + 1) % 2

  def setGridValue(self, row, col, player_index):
    if self.isGameOver():
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
