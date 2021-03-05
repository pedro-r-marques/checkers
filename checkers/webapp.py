""" Simple flask based webapp design to allow human vs computer play.
"""
import os

import flask
import uuid

from .checkers_lib import PyCheckersBoard as CheckersBoard
from .play_minmax import move_select


app = flask.Flask("checkers", static_url_path='')
app.secret_key = os.getenv("SECRET_KEY", "dev")

global_boards = dict()


def get_session_board():
    if 'uuid' not in flask.session:
        flask.session['uuid'] = uuid.uuid4()
    session_id = flask.session['uuid']
    if session_id not in global_boards:
        global_boards[session_id] = CheckersBoard()
    return global_boards[session_id]


@app.route('/checkers.js')
def script():
    return flask.send_from_directory('static', 'checkers.js')


@app.route('/', methods=['GET'])
def index():
    return flask.send_from_directory('static', 'index.html')


@app.route('/api/board',  methods=['GET'])
def get_board():
    board = get_session_board()
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
    board = get_session_board()
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
    board = get_session_board()

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
        move = move_select(board, player, None)
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
    board.move(move)

    return flask.make_response('OK', 200)


@app.route('/api/restart', methods=['POST'])
def board_init():
    if 'uuid' not in flask.session:
        return flask.make_response("Invalid session", 400)
    session_id = flask.session['uuid']
    if session_id not in global_boards:
        return flask.make_response("Invalid session", 400)
    global_boards[session_id] = CheckersBoard()
    return flask.make_response("OK", 200)


if __name__ == "__main__":
    app.run()
