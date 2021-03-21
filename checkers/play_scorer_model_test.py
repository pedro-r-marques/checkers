import unittest

from .py_checkers import PyCheckersBoard as CheckersBoard
from .play_scorer_model import TFScorerPlayer


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
