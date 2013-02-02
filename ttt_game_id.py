import math
import random
from google.appengine.ext import db

class GameCountDB(db.Model):
  count = db.IntegerProperty(required=True)


def IntToIDString(num_value):
  base = 36
  id = ''
  while True:
    digit = int(num_value % base)
    if digit < 10:
      digit = digit + 48
    else:
      digit = digit + 55
    id = id + chr(digit)
    num_value = math.floor(num_value / base)
    if num_value == 0:
      break
  return id


class GameID:
  id = ''
  position = 0

  def __init__(self, id, position):
    self.id = id
    self.position = position

  @staticmethod
  def MakeUniqueGameID():
    count_values = db.GqlQuery('SELECT * FROM GameCountDB')
    for count_db in count_values:
      count = count_db.count
      count_db.count = count_db.count + 1
      count_db.put()
      return GameID(IntToIDString(count), 0)

    game_count = GameCountDB(count = 0)
    game_count.put()
    return GameID(IntToIDString(0), 0)

  @staticmethod
  def MakeFromIDAndPositionString(id_pos_string):
    length = len(id_pos_string)
    if length < 2:
      return None
    id = id_pos_string[0:length - 1]
    pos = value[length - 1:]
    if pos.isdigit() and int(pos) != 0:
      return GameID(id, pos)
    return None
