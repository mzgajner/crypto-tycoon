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

def create_road(person=None):
  rv = {
    "type": "road",
  }
  rv["person"] = person if person else None
  return rv


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
@socketio.on('connect')
def handle_my_custom_event(player_data):
    players.append({
      'id': player_data['id']
    })
    if len(players) == 1:
      start()