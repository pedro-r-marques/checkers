import unittest
import random

from .checkers_lib import PyCheckersBoard as CheckersBoard
from .play_adaptative import MinMaxAdaptative


class MinMaxAdaptativeTest(unittest.TestCase):
    def setUp(self):
        random.seed(1337)

    def test_horizon(self):
        state = [
            [0, 0, 0, 1, 0, 0, 0, 1],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 2, 0, 0],
            [2, 0, 1, 0, 0, 0, 2, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 2, 0, 0],
            [0, 0, 0, 0, 0, 0, 2, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        algo = MinMaxAdaptative()
        m = algo.move_select(board, CheckersBoard.WHITE)
        print(m)
        # The goal is to avoid the move [(1, 2), (2, 3)]
        self.assertIsNotNone(m)

    def test_init_stage(self):
        state = [
            [0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 2, 0, 2],
            [2, 0, 2, 0, 0, 0, 0, 0],
            [0, 2, 0, 2, 0, 2, 0, 2],
            [2, 0, 2, 0, 2, 0, 2, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        algo = MinMaxAdaptative()
        m = algo.move_select(board, CheckersBoard.WHITE)
        print(m)
        self.assertIsNotNone(m)
