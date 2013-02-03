import cgi
import jinja2
import logging
import os
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
    if not game_id:
      return None
    game_grid = GameGrid.FindGameGridForID(game_id.id)
    if game_grid:
      return game_grid 
    if game_id.player_index != 0:
      return None
    game_grid = GameGrid(game_id.id)
    game_grid.save()
    return game_grid

  def getGameInfo(self, game_id):
    return 'game_id: ' + game_id.id + '/' + str(game_id.player_index)

  def getGameStatus(self, game_id, game_grid):
    status_list = []
    if game_id.player_index == 0:
      status_list.append('You are: O')
    else:
      status_list.append('You are: X')
    if game_grid.isGameOver():
      if game_grid.getWinningPlayerIndex() == game_id.player_index:
        status_list.append('you won!')
      else:
        status_list.append('you lost')
    elif game_id.player_index == game_grid.current_player_index:
      status_list.append('your turn')
    else:
      status_list.append('not your turn')
    return ", ".join(status_list)

  def makePage(self, game_id, message=None):
    game_grid = self.getGameGrid(game_id)
    if not game_grid:
      return jinja_environment.get_template('no_game.html').render()

    template_values = {
      'game_info': self.getGameInfo(game_id),
      'game_status': self.getGameStatus(game_id, game_grid),
      'grid_text': game_grid.getGridAsSimpleHTML(),
      'grid_html': game_grid.getGridAsHTML(game_id.player_index),
      'message': message,
    }
    template = jinja_environment.get_template('index.html')
    return template.render(template_values)

  def get(self, *args, **kwargs):
    game_id = self.getCurrentGameID(args)
    self.response.write(self.makePage(game_id))

  def parseSetCommand(self, words, row, col):
    if row and row.isdigit() and col and col.isdigit():
      return (int(row), int(col))
    if words and len(words) == 3 and words[0] == 'SET':
      if words[1].isdigit() and words[2].isdigit():
        return (int(words[1]), int(words[2]))
    return None

  def post(self, *args, **kwargs):
    game_id = self.getCurrentGameID(args)
    game_grid = self.getGameGrid(game_id)

    text_command = self.request.get('text_command')
    row = self.request.get('row')
    col = self.request.get('col')
    words = []
    if text_command:
      words = self.request.get('text_command').upper().split()

    message = ''
    if game_grid:
      setCommand = self.parseSetCommand(words, row, col)
      if setCommand:
        if game_grid.setGridValue(setCommand[0], setCommand[1], \
                                  game_id.player_index):
          game_grid.endCurrentTurn()
          game_grid.save()
        else:
          message = 'Error: invalid move'
      elif  len(words) == 2 and words[0] == 'INVITE':
        if game_id.player_index == 0:
          if words[1] == 'FRIEND':
            url = self.request.host_url + '/' + game_id.id + '1'
            message = 'Ask friend to go to ' + url
        else:
          message = 'Only the host player can invite.'
    self.response.write(self.makePage(game_id, message))


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}
app = webapp2.WSGIApplication([('/', MainPage),
                               (r'/([A-Z0-9]+)', MainPage)],
                              debug=True,
                              config=config)
