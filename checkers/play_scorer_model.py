import cachetools
import functools
import heapq
import os

import numpy as np

import tensorflow as tf
from tensorflow import keras

from .py_checkers import PyCheckersBoard as CheckersBoard
from .play_minmax import MinMaxPlayer


class MinMaxNode(object):
    """ Node in minmax tree.
    """

    __slots__ = ['board', 'player', 'n_children',
                 'score', 'heapq', 'parents', 'path']

    def __init__(self, board, player):
        self.board = board
        self.player = player    # next player to move
        self.n_children = 0
        self.score = None
        self.heapq = []
        self.parents = []
        self.path = []


class HeapQueueEntry(object):
    __slots__ = ['move', 'score', 'path']

    def __init__(self, move, score, path):
        self.move = move
        self.score = score
        self.path = path

    def __lt__(self, rhs):
        return self.score > rhs.score


class TFCallExecutor(object):
    BATCH_SIZE = 32
    BATCH_SLOTS = [8, 16, 24]

    def __init__(self, model, node_update_fn):
        self.model = model
        self.x_board = np.zeros((self.BATCH_SIZE, 8, 4, 4), dtype=np.bool)
        self.x_player = np.zeros((self.BATCH_SIZE, 2), dtype=np.bool)
        self.x_node_list = []
        self.x_move_list = []
        self.node_update_fn = node_update_fn

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
            self.update(node, self.x_move_list[i], y_pred[i].numpy())

        self.x_node_list = []
        self.x_move_list = []

    def update(self, node, move, y_pred):
        score = y_pred[1] - y_pred[2]
        player = node.player
        if player == CheckersBoard.BLACK:
            score = -score

        heapq.heappush(node.heapq, HeapQueueEntry(move, score, [move]))

        if len(node.heapq) == node.n_children:
            qhead = node.heapq[0]
            node.score = qhead.score
            node.path = qhead.path
            self.node_update_fn(node, qhead.path)


class TFScorerPlayer(object):
    DATADIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'data', 'score_model.0.1')

    def __init__(self, **kwargs):
        self.model = keras.models.load_model(self.DATADIR)
        self.exec = TFCallExecutor(self.model, self._node_update)
        self.max_depth = kwargs.get('max_depth', 4)
        self.cache = cachetools.Cache(maxsize=32*1024)

    def _node_update_parents(self, node, path):
        update_list = []
        for parent, move in node.parents:
            heapq.heappush(parent.heapq, HeapQueueEntry(
                move, -node.score, path))
            node.heapq = []

            if len(parent.heapq) == parent.n_children:
                qhead = parent.heapq[0]
                parent.score = qhead.score
                parent.path = qhead.path
                npath = [qhead.move] + qhead.path
                update_list.append((parent, npath))
        return update_list

    def _node_update(self, node, path):
        work_list = [(node, path)]
        while work_list:
            nwork_list = []
            for node, path in work_list:
                nwork_list.extend(self._node_update_parents(node, path))
            work_list = nwork_list

    def _run_minmax(self, node, depth):
        board = node.board
        moves = board.valid_moves(node.player)
        node.n_children = len(moves)
        if not moves:
            node.n_children = 1
            self.exec.enqueue(node, board, None, node.player)

        if depth == 0:
            for move in moves:
                nboard = CheckersBoard.copy(board)
                nboard.move(move)
                self.exec.enqueue(node, nboard, move, node.player)
            return

        opponent = CheckersBoard.WHITE if node.player == CheckersBoard.BLACK \
            else CheckersBoard.BLACK

        children = []
        for move in moves:
            nboard = CheckersBoard.copy(board)
            nboard.move(move)
            key = (hash(nboard), opponent, depth)
            if key in self.cache:
                child = self.cache[key]
                assert child.board == nboard
                if child.score is not None:
                    heapq.heappush(node.heapq, HeapQueueEntry(
                        move, -child.score, child.path))
                    continue
                child.parents.append((node, move))
                continue

            child = MinMaxNode(nboard, opponent)
            self.cache[key] = child
            child.parents.append((node, move))
            children.append(child)

        if len(node.heapq) == node.n_children:
            qhead = node.heapq[0]
            node.score = qhead.score
            self._node_update(node, qhead.path)
            return

        for child in children:
            self._run_minmax(child, depth - 1)

    def move_minmax(self, board, player):
        top_level = MinMaxNode(board, player)
        self._run_minmax(top_level, self.max_depth)
        self.exec.flush()

        if not top_level.heapq:
            return []

        qhead = top_level.heapq[0]
        score = qhead.score
        moves = [m.move for m in top_level.heapq if m.score == score]
        return moves

    def move_info(self, board, player, turn):
        top_level = MinMaxNode(board, player)
        self._run_minmax(top_level, self.max_depth)
        self.exec.flush()

        pq = top_level.heapq

        result = []

        while pq:
            node = heapq.heappop(pq)
            info = {
                'move': node.move,
                'score': float(node.score),
                'trace': node.path,
            }
            result.append(info)

        return result

    def move_select(self, board, player, turn=None):
        moves = self.move_minmax(board, player)
        if not moves:
            return None
        return moves[0]
