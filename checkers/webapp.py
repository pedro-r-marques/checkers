""" Simple flask based webapp design to allow human vs computer play.
"""
from flask import Flask, request, send_from_directory, jsonify, make_response

from .checkers import CheckersBoard
from .play import make_play

app = Flask("checkers", static_url_path='')

board = CheckersBoard()


@app.route('/checkers.js')
def script():
    return send_from_directory('static', 'checkers.js')


@app.route('/', methods=['GET'])
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/board',  methods=['GET'])
def get_board():
    response = {
        'board': board.pieces(),
        'pieces': board.count(),
    }
    return jsonify(response)


@app.route('/api/moves/<row>/<col>', methods=['GET'])
def get_valid_moves(row, col):
    coordinates = tuple(int(v) for v in [row, col])
    valid = all(v >= 0 and v < CheckersBoard.BOARD_SIZE for v in coordinates)
    if not valid:
        return make_response("Invalid coordinates", 400)
    moves = board.valid_position_moves(coordinates)
    return jsonify(moves)


@app.route('/api/move', methods=['POST'])
def make_move():
    data = request.get_json()
    if 'player' not in data:
        return make_response('No player id', 400)

    player = data['player']
    if player not in [CheckersBoard.WHITE, CheckersBoard.BLACK]:
        return make_response("Invalid player id", 400)

    if 'auto' in data and data['auto']:
        move = make_play(board, player)
        board.move(move)
        return jsonify(move)

    if 'start' not in data or 'end' not in data:
        return make_response('start and end positions must be specified')

    available = board.valid_position_moves(tuple(data['start']))
    opts = [m for m in available if m[-1] == tuple(data['end'])]
    if not opts:
        return make_response('invalid move', 400)
    board.move(opts[0])

    return make_response('OK', 200)


if __name__ == "__main__":
    app.run()
