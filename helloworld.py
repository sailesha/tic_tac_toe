import cgi
import logging
import math
import random
import webapp2

from google.appengine.ext import db
from webapp2_extras import sessions

def IntToUserID(num_value):
  base = 36
  user_id = ''
  while True:
    digit = int(num_value % base)
    if digit < 10:
      digit = digit + 48
    else:
      digit = digit + 55
    user_id = user_id + chr(digit)
    num_value = math.floor(num_value / base)
    if num_value == 0:
      break
  return user_id

def StringToUserIDAndPosition(value):
  if len(value) > 1:
    user_id = value[0:len(value) - 1]
    pos = value[len(value) - 1:]
    if pos.isdigit():
      pos_num = int(pos)
      if pos_num != 0:
        return (user_id, pos_num)
  return ('FFFF', 1)

class GameGrid(db.Model):
  grid = db.StringProperty()
  user_id = db.StringProperty(required=True)

class UserCount(db.Model):
  count = db.IntegerProperty(required=True)

def GameGridToHTML(grid):
  page = ''
  for row in range(0, 3):
    for col in range(0, 3):
      page = page + grid[row * 3 + col] + ', '
    page = page + '<BR>'
  return page

class MainPage(webapp2.RequestHandler):
  def __init__(self, request, response):
    webapp2.RequestHandler.__init__(self, request, response)

  def dispatch(self):
    # Get a session store for this request.
    self.session_store = sessions.get_store(request=self.request)

    try:
      # Dispatch the request.
      webapp2.RequestHandler.dispatch(self)
    finally:
      # Save all sessions.
      self.session_store.save_sessions(self.response)

  @webapp2.cached_property
  def session(self):
    # Returns a session using the default cookie key.
    return self.session_store.get_session()

  def makeUniqueUserID(self):
    values = db.GqlQuery('SELECT * FROM UserCount')
    for value in values:
      count = value.count
      value.count = value.count + 1
      value.put()
      return IntToUserID(count)
    user_count = UserCount(count = 0)
    user_count.put()
    return IntToUserID(0)

  def getCurrentUserIDAndPosition(self, *args):
    if len(args) > 0 and type(args[0]) is tuple:
      if len(args[0]) > 0 and type(args[0][0]) is str:
        return StringToUserIDAndPosition(args[0][0])
    user_id = self.session.get('user_id')
    if user_id:
      return (user_id, 0)
    user_id = self.makeUniqueUserID()
    self.session['user_id'] = user_id
    return (user_id, 0)

  def getGameGrid(self, user_id, position):
    grid_values = db.GqlQuery('SELECT * FROM GameGrid WHERE user_id in :1',
                              [user_id])
    for grid in grid_values:
      return grid
    if position != 0:
      return None
    grid = GameGrid(user_id = user_id)
    grid.grid = '000000000'
    grid.put()
    return grid

  def makePage(self, user_id, position):
    game_grid = self.getGameGrid(user_id, position)

    page = '<HTML><BODY>'
    page = 'user_id: ' + user_id + '<BR>'
    if game_grid:
      page = page + GameGridToHTML(game_grid.grid)
      page = page + """<FORM method="post">
                         <textarea name="content"></textarea>
                         <input type="submit" value="Submit">
                       </FORM>"""
    else:
      page = page + 'Error: No game found<BR>'
    page = page + '</BODY></HTML>'
    return page

  def get(self, *args, **kwargs):
    (user_id, position) = self.getCurrentUserIDAndPosition(args)
    self.response.write(self.makePage(user_id, position))

  def post(self, *args, **kwargs):
    (user_id, position) = self.getCurrentUserIDAndPosition(args)
    content = self.request.get('content').split(',')
    row = int(content[0])
    col = int(content[1])
    value = content[2]
    index = row * 3 + col

    game_grid = self.getGameGrid(user_id, position)
    if game_grid:
      game_grid.grid = game_grid.grid[0:index] + value + \
                       game_grid.grid[(index + 1):]
      game_grid.put()

    self.response.write(self.makePage(user_id, position))

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}
app = webapp2.WSGIApplication([('/', MainPage),
                               (r'/([A-Z0-9]+)', MainPage)],
                              debug=True,
                              config=config)
