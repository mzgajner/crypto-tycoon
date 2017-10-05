import random
import threading
import collections

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

if __name__ == '__main__':
    socketio.run(app)


# land content : {type: 'building', owner: person_id}
def create_land(content=None):
  rv = {
    "type": "land"
  }
  rv["content"] = content if content else None
  return rv

def create_road(people=None):
  rv = {
    "type": "road",
  }
  rv["content"] = people if people else []
  return rv

def create_person():
  return {
    "type": "person",
    "prev": None
    "money": random.ranint(50, 100)
  }

LAND = create_land
ROAD = create_road


def append_mid(world):
  world.extend([
    [ROAD()] * 27,
    [LAND()] + [ROAD(), LAND(), LAND()] * 8 + [ROAD(), LAND()],
    [LAND()] + [ROAD(), LAND(), LAND()] * 8 + [ROAD(), LAND()],
  ])

world = [
  # first
  [LAND()] + [ROAD(), LAND(), LAND()] * 8 + [ROAD(), LAND()],
]
for i in range(5):
  append_mid(world)
world.extend([
  [ROAD()] * 27,
  [LAND()] + [ROAD(), LAND(), LAND()] * 8 + [ROAD(), LAND()]
])
print world

players = []
start_money = 1000
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
apply_moves = collections.defaultdict(list)

def is_type(i, j, type_):
  if i < 0 or i >= len(world): return False
  if j < 0 or j >= len(world[0]): return False
  return world[i][j]["type"] == type_

def get_next_step_options(i, j, prev):
  return [
    (i + dir_i, j + dir_j)
    for dir_i, dir_j in directions
    if is_type(i+dir_i, j+dir_j, "road") and not (i+dir_i, j+dir_j) == prev
  ]
  
def move_person(i, j, person):
  prev = person["prev"]
  step_options = get_next_step_options(i, j, prev)
  if not step_options:
    return
  rnd = random.randint(0, len(step_options))
  chosen_step = step_options[rnd]
  person["prev"] = (i, j)
  apply_moves[chosen_step].append(person)

def apply_people_moves():
  for (i,j), people in apply_moves.items():
    world[i][j]["content"] = people

def move_people():
  for i, row in enumerate(world):
    for j, field in enumerate(row):
      if field["type"] == "road":
        for person in field["content"]:
          move_person(i, j, person)
        field["content"] = None
  apply_people_moves()

def generate_people():
  N = 3
  for j, field in enumerate(world[0]):
    if is_type(0, j, "road"):
      if random.random() > 0.3:
        world[0][j]["content"].append(create_person())

class Ticker(threading.Thread):

  def __init__(self, secs):
    self.secs = secs

  def do_tick():
    move_people()
    generate_people()
  
  def run(self):
    while True:
      time.sleep(self.secs)
      self.do_tick()
      

def ticker():
  move_people()
  generate_people()

def start():
  emit(
    'start',
    {
      'world': world,
      'start_money': start_money
    },
    broadcast=True
  )


# socket handlers
@socketio.on('register')
def register(player_data):
    print player_data
    players.append({
      'id': player_data['id']
    })
    if len(players) > 0:
      start()