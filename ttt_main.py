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
        return GameID.MakeFromIDAndPlayerIndexString(args[0][0])
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
    if game_id.player_idex != 0:
      return None
    game_grid = GameGrid(game_id.id)
    game_grid.save()
    return game_grid

  def makePage(self, game_id, message=None):
    game_grid = self.getGameGrid(game_id)

    page = '<HTML><BODY>'
    page = 'game_id: ' + game_id.id + '/' + str(game_id.player_index) + '<BR>'
    if game_id.player_index == 0:
      page = page + 'You are: O'
    else:
      page = page + 'You are: X'
    game_over = game_grid.isGameOver()
    if game_over[0]:
      if game_over[1] == game_id.player_index:
        page = page + ', you won!'
      else:
        page = page + ', you lost'
    elif game_id.player_index == game_grid.current_player_index:
      page = page + ', your turn'
    else:
      page = page + ', not your turn'
    page = page + '<BR>'

    if game_grid:
      page = page + game_grid.getGridAsHTML()
      page = page + """<FORM method="post">
                         <textarea name="text_command"></textarea>
                         <input type="submit" value="Submit">
                       </FORM>"""
    else:
      page = page + 'Error: No game found<BR>'
    if message:
      page = page + message + '<BR>'
    page = page + '</BODY></HTML>'
    return page

  def get(self, *args, **kwargs):
    game_id = self.getCurrentGameID(args)
    self.response.write(self.makePage(game_id))

  def post(self, *args, **kwargs):
    game_id = self.getCurrentGameID(args)
    game_grid = self.getGameGrid(game_id)
    words = self.request.get('text_command').upper().split()
    message = ''
    if game_grid and len(words) > 0:
      if words[0] == 'SET' and len(words) == 3:
        row = int(words[1])
        col = int(words[2])
        if game_grid.setGridValue(row, col, game_id.player_index):
          game_grid.endCurrentTurn()
          game_grid.save()
        else:
          message = 'Error: invalid move'
      elif words[0] == 'INVITE' and len(words) == 2:
        if game_id.player_index == 0:
          if words[1] == 'FRIEND':
            url = self.request.host_url + '/' + game_id.id + '1'
            message = 'Ask friend to go to ' + url
        else:
          message = 'Only the host player can invite.'
    self.response.write(self.makePage(game_id, message))

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}
app = webapp2.WSGIApplication([('/', MainPage),
                               (r'/([A-Z0-9]+)', MainPage)],
                              debug=True,
                              config=config)
