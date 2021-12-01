import os
import random
import json

import cachetools
import numpy as np
import urllib3

from .py_checkers import PyCheckersBoard as CheckersBoard
from .minmax_tree import MinMaxTreeExecutor, ScorerExecutor


class TFCallExecutor(ScorerExecutor):
    BATCH_SIZE = 32
    BATCH_SLOTS = [8, 16, 24]

    def __init__(self, uri):
        super().__init__()
        self.http = urllib3.PoolManager()
        self.uri = uri
        self.x_board = np.zeros((self.BATCH_SIZE, 8, 4, 4), dtype=bool)
        self.x_player = np.zeros((self.BATCH_SIZE, 2), dtype=bool)
        self.x_node_list = []
        self.x_move_list = []
        self.x_key_list = []
        self.cache = cachetools.LRUCache(maxsize=32*1024)

    @staticmethod
    def _make_features(board, player, x_board, x_player):
        x_board.fill(0)
        for piece in board.pieces():
            row = piece[0]
            col = piece[1] // 2
            x_board[row][col][piece[2] - 1] = True

        x_player.fill(0)
        x_player[player - 1] = True

    def predict(self, args):
        data = {
            'inputs': {
                'input_31': args[0].astype(float).tolist(),
                'input_32': args[1].astype(float).tolist(),
            },
        }
        r = self.http.request('POST', self.uri + ':predict',
                              body=json.dumps(data).encode('utf-8'))
        if r.status != 200:
            raise Exception(r.data)

        resp = json.loads(r.data.decode('utf-8'))
        arr = np.array(resp['outputs'])
        return arr

    def enqueue(self, node, board, move, player):
        key = (hash(board), player)
        if key in self.cache:
            self.update(node, move, self.cache[key])
            return

        i = len(self.x_node_list)
        assert i < self.BATCH_SIZE
        self._make_features(board, player, self.x_board[i], self.x_player[i])
        self.x_node_list.append(node)
        self.x_move_list.append(move)
        self.x_key_list.append(key)
        if len(self.x_node_list) == self.BATCH_SIZE:
            self.flush()

    def flush(self):
        batch_size = len(self.x_node_list)

        for i in self.BATCH_SLOTS:
            if batch_size < i:
                batch_size = i

        data = [arr[:batch_size] for arr in [self.x_board, self.x_player]]
        y_pred = self.predict(data)

        for i, node in enumerate(self.x_node_list):
            score = y_pred[i, 1] - y_pred[i, 2]
            player = node.player
            if player == CheckersBoard.BLACK:
                score = -score
            key = self.x_key_list[i]
            self.cache[key] = score
            self.update(node, self.x_move_list[i], score)

        self.x_node_list = []
        self.x_move_list = []
        self.x_key_list = []


class TFScorerPlayer(MinMaxTreeExecutor):
    PORT = 8501

    def __init__(self, **kwargs):
        hostname = os.getenv('TF_SERVING_HOST') or 'localhost'
        self.exec = TFCallExecutor(
            f'http://{hostname}:{self.PORT}/v1/models/score_model')
        super().__init__(self.exec, max_depth=kwargs.get('max_depth', 4))

    def move_select(self, board, player, turn=None):
        moves = self.move_minmax(board, player)
        if not moves:
            return None
        if len(moves) > 1:
            return random.choice(moves)
        return moves[0]
