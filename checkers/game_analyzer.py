""" Flask based app to display the moves of a logged game and analyze the
    algorithm decision.
"""

import argparse
import flask
import pickle
import os

from .checkers_lib import PyCheckersBoard as CheckersBoard
from .play_minmax import MinMaxPlayer

source_dir = os.path.dirname(os.path.abspath(__file__))
app = flask.Flask("analyzer", static_folder=os.path.join(source_dir, 'static'))
log_history = None

algorithm = MinMaxPlayer()

@app.route('/', methods=['GET'])
def index():
    return flask.redirect("/static/analyzer.html", 303)


def board_pieces(board):
    pieces = []
    for i, piece in enumerate(board):
        if piece == 0:
            continue
        row = i // 8
        col = i & 7
        pieces.append((row, col, piece))
    return pieces


def make_board(state_bin):
    """ Create an initialized CheckersBoard
    """
    board = CheckersBoard()
    state = [[] for _ in range(8)]
    for i in range(8):
        start = i * 8
        state[i] = [int(x) for x in state_bin[start:start + 8]]
    board.initialize(state)
    return board


def last_piece_count(state_bin, last_move):
    board = make_board(state_bin)
    board.move(last_move)
    return board.count()


@app.route('/api/move/<turn>', methods=['GET'])
def get_move_info(turn):
    try:
        turn = int(turn)
    except Exception:
        flask.make_response("turn parameter must be an integer", 400)

    if turn >= len(log_history):
        return flask.make_response("Invalid move number", 400)

    log_entry = log_history[turn]
    last_entry = log_history[-1]

    board = make_board(log_entry[0])

    response = {
        'board': board_pieces(log_entry[0]),
        'n_turns': len(log_history),
        'player': log_entry[2],
        'move': log_entry[3],
        'result': last_piece_count(last_entry[0], last_entry[3]),
        'debug': algorithm.move_info(board, log_entry[2], log_entry[1])
    }
    return flask.jsonify(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Game log to analyze")
    args = parser.parse_args()
    with open(args.filename, 'rb') as fp:
        log_history = pickle.load(fp)

    app.run()
