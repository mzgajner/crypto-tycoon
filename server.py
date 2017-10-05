import time
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
    "prev": None,
    "money": random.randint(50, 100),
    "steps": 0,
    "id": random.randint(1,1000000)
  }

def create_bank(player_id):
  return {
    "type": "building",
    "player_id": player_id,
    "currency": player_curs[player_id]
  }

LAND = create_land
ROAD = create_road

def build_road(n):
  rv = []
  for i in range(n):
    rv.append(ROAD())
  return rv

def build_road_block(n):
  rv = []
  for _ in range(n):
    rv.extend([ROAD(), LAND(), LAND()])
  return rv

def append_mid(world):
  world.extend([
    build_road(27),
    [LAND()] + build_road_block(8) + [ROAD(), LAND()],
    [LAND()] + build_road_block(8) + [ROAD(), LAND()],
  ])

world = [
  # first
  [LAND()] + build_road_block(8) + [ROAD(), LAND()],
]
for i in range(5):
  append_mid(world)
world.extend([
  build_road(27),
  [LAND()] + build_road_block(8) + [ROAD(), LAND()]
])
print world

players = {}
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
  
def get_bank_options(i, j):
  return [
    (i + dir_i, j + dir_j)
    for dir_i, dir_j in directions
    if is_type(i+dir_i, j+dir_j, "land") and world[i+dir_i][j+dir_j]["content"]
  ]

def visit_bank(cords, person):
  i, j = map(int, cords)
  bank_options = get_bank_options(i, j)
  if not bank_options:
    return False
  if not 0.5 * (random.random() * (person["steps"]/10.0)) > 0.4:
    return False
  rnd = random.randint(0, len(bank_options) - 1)
  i1, j1 = map(int, bank_options[rnd])
  print i1,j1
  print world[i1][j1]
  bank_owner = world[i1][j1]["content"][0]["player_id"]
  players[bank_owner] += person["money"]
  return True


def move_person(i, j, person):
  prev = person["prev"]
  step_options = get_next_step_options(i, j, prev)
  if not step_options:
    return
  rnd = random.randint(0, len(step_options) - 1)
  chosen_step = step_options[rnd]
  person["prev"] = (i, j)
  person["steps"] += 1
  if not visit_bank(chosen_step, person):
    apply_moves[chosen_step].append(person)

def apply_people_moves():
  for (i,j), people in apply_moves.items():
    world[i][j]["content"] = people

def move_people():
  apply_moves.clear()
  for i, row in enumerate(world):
    for j, field in enumerate(row):
      if field["type"] == "road":
        for person in field["content"]:
          move_person(i, j, person)
        field["content"] = []
  # print apply_moves
  apply_people_moves()

def generate_people():
  def generate_for_row(row):
    for j, field in enumerate(row):
      if is_type(0, j, "road"):
        if random.random() < 0.1:
          row[j]["content"].append(create_person())
  generate_for_row(world[0])
  generate_for_row(world[len(world) -1])

class Ticker(threading.Thread):

  def __init__(self, secs):
    self.secs = secs

  def do_tick(self):
    move_people()
    generate_people()
    update()
  
  def run(self):
    while True:
      time.sleep(self.secs)
      self.do_tick()


def update():
  emit(
    'update',
    {
      'world': world,
      'money': players
    },
    broadcast=True
  )

player_curs = {}
curs = ['btc', 'etc']
# socket handlers
@socketio.on('register')
def register(player_data):
  print player_data
  players[player_data["id"]] = start_money
  player_curs[player_data["id"]] = curs.pop()
  if len(players) == 2:
    Ticker(1).run()

@socketio.on('build')
def build(json):
  print "noter"
  i, j = json["position"]
  money = json["money"]
  player_id = json["player_id"]
  if not is_type(i,j,"land") or world[i][j]["content"] is not None:
    return
  if money >= players[player_id]:
    players[player_id] -= 200
  world[i][j]["content"] = [create_bank(player_id)]
  # return new money state
  print "new money:", players[player_id]
  update()
  return players[player_id]
  