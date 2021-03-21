import heapq
import unittest

from .py_checkers import PyCheckersBoard as CheckersBoard
from .play_scorer_model import TFScorerPlayer, HeapQueueEntry
from .py_scorer import PyScorer


class MockExecutor(object):
    def __init__(self, cb_update_fn, batch_size=3):
        self.x_node_list = []
        self.x_move_list = []
        self.x_scores = []
        self.cb_update_fn = cb_update_fn
        self.batch_size = batch_size
        self.scorer = PyScorer()

    def enqueue(self, node, board, move, player):
        self.x_node_list.append(node)
        self.x_move_list.append(move)
        self.x_scores.append(self.scorer.score(board, player))
        if len(self.x_node_list) == self.batch_size:
            self.flush()

    def flush(self):
        for node, move, score in zip(
                self.x_node_list, self.x_move_list, self.x_scores):
            self.update(node, move, score)
        self.x_node_list = []
        self.x_move_list = []
        self.x_scores = []

    def update(self, node, move, score):
        heapq.heappush(node.heapq, HeapQueueEntry(move, score, [move]))

        if len(node.heapq) == node.n_children:
            qhead = node.heapq[0]
            node.score = qhead.score
            node.path = qhead.path
            self.cb_update_fn(node, qhead.path)


class PlayScorerMinMaxTest(unittest.TestCase):
    def test_update_1(self):
        state = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 2, 0, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        player = TFScorerPlayer(max_depth=1)
        player.exec = MockExecutor(player._node_update)
        info = player.move_info(board, CheckersBoard.BLACK, None)
        print(info)
        moves = player.move_minmax(board, CheckersBoard.BLACK)
        self.assertEqual(moves, [[(5, 2), (4, 3)], [(5, 4), (4, 5)]])

    def test_update_2(self):
        state = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 2, 0, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        player = TFScorerPlayer(max_depth=2)
        player.exec = MockExecutor(player._node_update)
        moves = player.move_minmax(board, CheckersBoard.BLACK)
        self.assertEqual(moves, [[(5, 2), (4, 3)]])

    def test_update_3(self):
        state = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 2, 0, 0],
            [2, 0, 0, 0, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        player = TFScorerPlayer(max_depth=2)
        player.exec = MockExecutor(player._node_update)
        moves = player.move_minmax(board, CheckersBoard.BLACK)
        self.assertEqual(moves, [[(4, 5), (3, 4)], [(4, 5), (3, 6)]])

    def test_update_4(self):
        state = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 2, 0, 2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        player = TFScorerPlayer(max_depth=4)
        player.exec = MockExecutor(player._node_update)
        info = player.move_info(board, CheckersBoard.BLACK, None)
        print(info)
        max_score = max(x['score'] for x in info)
        moves = [x['move'] for x in info if x['score'] == max_score]
        self.assertNotIn([(5, 0), (4, 1)], moves)
        self.assertNotIn([(5, 4), (4, 3)], moves)

    def test_horizon(self):
        state = [
            [0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 2, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 2, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 2],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 2],
            [2, 0, 2, 0, 0, 0, 2, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        player = TFScorerPlayer(max_depth=4)
        player.exec = MockExecutor(player._node_update)
        moves = player.move_minmax(board, CheckersBoard.WHITE)
        self.assertEqual(moves, [[(3, 4), (4, 3)]])

    def test_no_move(self):
        state = [
            [0, 0, 0, 4, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 0, 0],
            [2, 0, 2, 0, 0, 0, 0, 0],
            [0, 2, 0, 2, 0, 2, 0, 2],
            [2, 0, 0, 0, 2, 0, 2, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        player = TFScorerPlayer(max_depth=4)
        player.exec = MockExecutor(player._node_update)
        moves = player.move_minmax(board, CheckersBoard.WHITE)
        self.assertEqual(moves, [None])


class PlayScorerModelTest(unittest.TestCase):
    def setUp(self):
        self.algorithm = TFScorerPlayer()

    def test_horizon(self):
        state = [
            [0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 2, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 2, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 2],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 2],
            [2, 0, 2, 0, 0, 0, 2, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        move = self.algorithm.move_select(board, CheckersBoard.WHITE, None)
        self.assertNotIn(move, [
            [(1, 0), (2, 1)], [(1, 4), (2, 3)],
            [(5, 2), (6, 1)], [(5, 2), (6, 3)]
        ])

    def test_horizon_info(self):
        state = [
            [0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 2, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 2, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 2],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 2],
            [2, 0, 2, 0, 0, 0, 2, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        result = self.algorithm.move_info(board, CheckersBoard.WHITE, None)
        self.assertTrue(result)
