""" Simple flask based webapp design to allow human vs computer play.
"""
import datetime
import os
import uuid

import cachetools
import flask

from .py_checkers import PyCheckersBoard as CheckersBoard
from .play_minmax import MinMaxPlayer
from .play_probability import StatsPlayer
from .logger import GameLogger


class SessionState():
    def __init__(self):
        self.board = CheckersBoard()
        self.tstamp = datetime.datetime.now()
        self.log = GameLogger()
        self.turn = 0

    def log_move(self, player, move):
        self.log.log(self.board, self.turn, player, move)
        filename = self.tstamp.strftime("%Y%m%d%H%M%S%f") + ".dat"
        self.log.save(os.path.join(os.getenv('SESSION_LOG_DIR', ""), filename))
        self.turn += 1


source_dir = os.path.dirname(os.path.abspath(__file__))
app = flask.Flask("checkers", static_url_path='',
                  static_folder=os.path.join(source_dir, 'static'))
app.secret_key = os.getenv("SECRET_KEY", "dev")


global_sessions = cachetools.TTLCache(maxsize=1024, ttl=60*30)

algorithm = StatsPlayer(select_best=True)


def get_session_state():
    if 'uuid' not in flask.session:
        flask.session['uuid'] = uuid.uuid4()
    session_id = flask.session['uuid']
    if session_id not in global_sessions:
        global_sessions[session_id] = SessionState()
    return global_sessions[session_id]


@app.route('/', methods=['GET'])
def index():
    return flask.redirect('index.html', 303)


@app.route('/api/board',  methods=['GET'])
def get_board():
    state = get_session_state()
    board = state.board
    response = {
        'board': board.pieces(),
        'pieces': board.count(),
    }
    return flask.jsonify(response)


@app.route('/api/moves/<row>/<col>', methods=['GET'])
def get_valid_moves(row, col):
    coordinates = tuple(int(v) for v in [row, col])
    valid = all(v >= 0 and v < CheckersBoard.BOARD_SIZE for v in coordinates)
    if not valid:
        return flask.make_response("Invalid coordinates", 400)
    state = get_session_state()
    board = state.board
    pieces = board.count()
    if any(c == 0 for c in pieces):
        return flask.make_response("Game over", 400)
    piece = board.get_position(coordinates)
    if piece in [CheckersBoard.WHITE, CheckersBoard.WHITE_KING]:
        player = CheckersBoard.WHITE
    elif piece in [CheckersBoard.BLACK, CheckersBoard.BLACK_KING]:
        player = CheckersBoard.BLACK
    else:
        return flask.make_response("Empty position", 400)
    player_moves = board.valid_moves(player)
    moves = [m for m in player_moves if m[0] == coordinates]
    return flask.jsonify(moves)


@app.route('/api/move', methods=['POST'])
def make_move():
    state = get_session_state()
    board = state.board

    pieces = board.count()
    if any(c == 0 for c in pieces):
        return flask.make_response("Game over", 400)

    data = flask.request.get_json()
    if 'player' not in data:
        return flask.make_response('No player id', 400)

    player = data['player']
    if player not in [CheckersBoard.WHITE, CheckersBoard.BLACK]:
        return flask.make_response("Invalid player id", 400)

    if 'auto' in data and data['auto']:
        move = algorithm.move_select(board, player, None)
        if not app.testing:
            state.log_move(player, move)
        board.move(move)
        return flask.jsonify(move)

    if 'start' not in data or 'end' not in data:
        return flask.make_response('start and end positions must be specified')

    player_moves = board.valid_moves(player)

    move = None
    for m in player_moves:
        if m[0] == tuple(data['start']) and m[-1] == tuple(data['end']):
            move = m
            break

    if move is None:
        return flask.make_response('invalid move', 400)
    if not app.testing:
        state.log_move(player, move)
    board.move(move)

    return flask.make_response('OK', 200)


@app.route('/api/restart', methods=['POST'])
def board_init():
    if 'uuid' not in flask.session:
        return flask.make_response("Invalid session", 400)
    session_id = flask.session['uuid']
    if session_id not in global_sessions:
        return flask.make_response("Invalid session", 400)
    global_sessions[session_id] = SessionState()
    return flask.make_response("OK", 200)


if __name__ == "__main__":
    app.run()
