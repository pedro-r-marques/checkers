import functools
import os

import numpy as np

import tensorflow as tf
from tensorflow import keras

from .py_checkers import PyCheckersBoard as CheckersBoard
from .play_minmax import MinMaxPlayer


def _make_features(board, player, x_data):
    x_board = np.zeros((8, 4, 4), dtype=bool)
    for piece in board.pieces():
        row = piece[0]
        col = piece[1] // 2
        x_board[row][col][piece[2] - 1] = True
    x_player = np.zeros((2,), dtype=bool)
    x_player[player - 1] = True
    x_data[0].append(tf.convert_to_tensor(x_board))
    x_data[1].append(tf.convert_to_tensor(x_player))


def _model_score(model, board, player):
    x_data = [[], []]
    _make_features(board, player, x_data)
    x_data_arr = [tf.stack(x) for x in x_data]
    y_pred = model(x_data_arr)
    scores = y_pred[:, 1] - y_pred[:, 2]
    if player == CheckersBoard.BLACK:
        scores = -scores
    return scores[0]


@functools.lru_cache(maxsize=32*1024)
def move_minmax(model, board, player, depth):
    moves = board.valid_moves(player)
    if not moves:
        score = _model_score(model, board, player)
        return [None], [score], 0

    if depth == 0:
        x_data = [[], []]
        for move in moves:
            nboard = CheckersBoard.copy(board)
            nboard.move(move)
            _make_features(nboard, player, x_data)

        x_data_arr = [tf.stack(x) for x in x_data]
        y_pred = model(x_data_arr)
        scores = y_pred[:, 1] - y_pred[:, 2]
        if player == CheckersBoard.BLACK:
            scores = -scores
        return moves, scores, np.argmax(scores)

    opponent = CheckersBoard.WHITE if player == CheckersBoard.BLACK \
        else CheckersBoard.BLACK

    scores = []
    for move in moves:
        nboard = CheckersBoard.copy(board)
        nboard.move(move)
        _, opp_scores, ix = move_minmax(
            model, nboard, opponent, depth - 1)
        score = -opp_scores[ix]
        scores.append(score)

    return moves, scores, np.argmax(scores)


class TFScorerPlayer(object):
    DATADIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'data', 'score_model.0.1')

    def __init__(self, **kwargs):
        self.model = keras.models.load_model(self.DATADIR)
        self.max_depth = kwargs.get('max_depth', 4)

    @tf.function
    def predict(self, args):
        return self.model(args)

    def move_info(self, board, player, turn):
        min_max_player = MinMaxPlayer()
        base_info = min_max_player.move_info(board, player, turn)

        x_data = [[], []]
        for info in base_info:
            nboard = CheckersBoard.copy(board)
            nboard.move(info['move'])
            _make_features(nboard, player, x_data)

        x_data_arr = [np.stack(x) for x in x_data]
        y_pred = self.model.predict(x_data_arr)

        for info, y_s in zip(base_info, y_pred):
            info['tf_score'] = y_s.tolist()

        return base_info

    def move_select(self, board, player, turn=None):
        moves, scores, ix = move_minmax(
            self.predict, board, player, self.max_depth)
        if not moves:
            return None
        return moves[ix]
