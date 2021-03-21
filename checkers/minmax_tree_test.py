import random
import unittest

from .minmax_tree import MinMaxTreeExecutor, ScorerExecutor
from .py_checkers import PyCheckersBoard as CheckersBoard
from .py_scorer import PyScorer
from .play_minmax import MinMaxPlayer


class PyScorerExecutor(ScorerExecutor):
    def __init__(self, batch_size=3):
        super().__init__()
        self.x_node_list = []
        self.x_move_list = []
        self.x_scores = []
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


class MinMaxTreeTest(unittest.TestCase):
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
        player = MinMaxTreeExecutor(PyScorerExecutor(), max_depth=1)
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
        player = MinMaxTreeExecutor(PyScorerExecutor(), max_depth=2)
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
        player = MinMaxTreeExecutor(PyScorerExecutor(), max_depth=2)
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
        player = MinMaxTreeExecutor(PyScorerExecutor(), max_depth=4)
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
        player = MinMaxTreeExecutor(PyScorerExecutor(), max_depth=4)
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
        player = MinMaxTreeExecutor(PyScorerExecutor(), max_depth=4)
        moves = player.move_minmax(board, CheckersBoard.WHITE)
        self.assertEqual(moves, [None])


class MinMaxCompareTest(unittest.TestCase):
    def setUp(self):
        random.seed(1337)

    def test_play_game(self):
        reference_player = MinMaxPlayer()
        tree_player = MinMaxTreeExecutor(PyScorerExecutor())

        board = CheckersBoard()

        for turn in range(256):
            if turn % 2 == 0:
                player = CheckersBoard.BLACK
            else:
                player = CheckersBoard.WHITE

            moves, scores = reference_player.move_scores(board, player, turn)
            tree_selected = tree_player.move_minmax(board, player)
            max_score = max(scores)
            ref_selected = [moves[i] for i, s in enumerate(scores)
                            if s == max_score]
            self.assertCountEqual(ref_selected, tree_selected)

            if moves:
                weights = reference_player.make_weights(scores)
                mv = random.choices(moves, weights=weights)[0]
                board.move(mv)

            counts = board.count()
            if any(c == 0 for c in counts):
                break
