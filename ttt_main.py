import cgi
import logging
import webapp2
from webapp2_extras import sessions
from ttt_game_grid import GameGrid
from ttt_game_id import GameID

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

  def getCurrentGameID(self, *args):
    if len(args) > 0 and type(args[0]) is tuple:
      if len(args[0]) > 0 and type(args[0][0]) is str:
        return GameID.MakeFromIDAndPositionString(args[0][0])
    game_id = self.session.get('game_id')
    if game_id:
      return GameID(game_id, 0)
    game_id = GameID.MakeUniqueGameID()
    self.session['game_id'] = game_id.id
    return game_id

  def getGameGrid(self, game_id):
    game_grid = GameGrid.FindGameGridForID(game_id.id)
    if game_grid:
      return game_grid 
    if game_id.position != 0:
      return None
    game_grid = GameGrid(game_id.id)
    game_grid.save()
    return game_grid

  def makePage(self, game_id):
    game_grid = self.getGameGrid(game_id)

    page = '<HTML><BODY>'
    page = 'game_id: ' + game_id.id + '/' + str(game_id.position) + '<BR>'
    if game_grid:
      page = page + game_grid.getGridAsHTML()
      page = page + """<FORM method="post">
                         <textarea name="content"></textarea>
                         <input type="submit" value="Submit">
                       </FORM>"""
    else:
      page = page + 'Error: No game found<BR>'
    page = page + '</BODY></HTML>'
    return page

  def get(self, *args, **kwargs):
    game_id = self.getCurrentGameID(args)
    self.response.write(self.makePage(game_id))

  def post(self, *args, **kwargs):
    game_id = self.getCurrentGameID(args)
    content = self.request.get('content').split(',')
    row = int(content[0])
    col = int(content[1])
    value = int(content[2])
    game_grid = self.getGameGrid(game_id)
    if game_grid:
      game_grid.setGridValue(row, col, value)
      game_grid.save()
    self.response.write(self.makePage(game_id))

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}
app = webapp2.WSGIApplication([('/', MainPage),
                               (r'/([A-Z0-9]+)', MainPage)],
                              debug=True,
                              config=config)
