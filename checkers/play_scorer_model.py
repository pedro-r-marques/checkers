import os

import numpy as np

import tensorflow as tf
from tensorflow import keras

from .py_checkers import PyCheckersBoard as CheckersBoard
from .minmax_tree import MinMaxTreeExecutor, ScorerExecutor


class TFCallExecutor(ScorerExecutor):
    BATCH_SIZE = 32
    BATCH_SLOTS = [8, 16, 24]

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.x_board = np.zeros((self.BATCH_SIZE, 8, 4, 4), dtype=np.bool)
        self.x_player = np.zeros((self.BATCH_SIZE, 2), dtype=np.bool)
        self.x_node_list = []
        self.x_move_list = []

    @staticmethod
    def _make_features(board, player, x_board, x_player):
        x_board.fill(0)
        for piece in board.pieces():
            row = piece[0]
            col = piece[1] // 2
            x_board[row][col][piece[2] - 1] = True

        x_player.fill(0)
        x_player[player - 1] = True

    @tf.function
    def predict(self, args):
        return self.model(args)

    def enqueue(self, node, board, move, player):
        i = len(self.x_node_list)
        assert i < self.BATCH_SIZE
        self._make_features(board, player, self.x_board[i], self.x_player[i])
        self.x_node_list.append(node)
        self.x_move_list.append(move)
        if len(self.x_node_list) == self.BATCH_SIZE:
            self.flush()

    def flush(self):
        batch_size = len(self.x_node_list)

        for i in self.BATCH_SLOTS:
            if batch_size < i:
                batch_size = i

        data = [tf.convert_to_tensor(arr[:batch_size])
                for arr in [self.x_board, self.x_player]]
        y_pred = self.predict(data)

        for i, node in enumerate(self.x_node_list):
            score = y_pred[i, 1] - y_pred[i, 2]
            score = score.numpy()
            player = node.player
            if player == CheckersBoard.BLACK:
                score = -score
            self.update(node, self.x_move_list[i], score)

        self.x_node_list = []
        self.x_move_list = []


class TFScorerPlayer(MinMaxTreeExecutor):
    DATADIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'data', 'score_model.0.1')

    def __init__(self, **kwargs):
        self.model = keras.models.load_model(self.DATADIR)
        self.exec = TFCallExecutor(self.model)
        super().__init__(self.exec, max_depth=kwargs.get('max_depth', 4))

    def move_select(self, board, player, turn=None):
        moves = self.move_minmax(board, player)
        if not moves:
            return None
        return moves[0]
