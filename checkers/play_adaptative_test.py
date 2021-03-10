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
        self.assertIsNotNone(m)

    def test_2kings(self):
        state = [
            [0, 0, 0, 0, 0, 4, 0, 0],
            [0, 0, 0, 0, 0, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        algo = MinMaxAdaptative()
        m = algo.move_select(board, CheckersBoard.WHITE)
        self.assertIsNotNone(m)

    def test_no_moves(self):
        pieces = [[0, 5, 1], [0, 7, 1], [1, 2, 1], [2, 1, 1],
                  [2, 3, 1], [3, 0, 2], [4, 7, 1], [5, 4, 1]]
        state = [[0] * 8 for _ in range(8)]
        for row, col, piece in pieces:
            state[row][col] = piece
        board = CheckersBoard()
        board.initialize(state)
        algo = MinMaxAdaptative()
        m = algo.move_select(board, CheckersBoard.BLACK)
        self.assertIsNone(m)

    def test_slow(self):
        pieces = [[2, 5, 3], [3, 0, 3], [4, 5, 4], [5, 0, 2], [7, 6, 4]]
        state = [[0] * 8 for _ in range(8)]
        for row, col, piece in pieces:
            state[row][col] = piece
        board = CheckersBoard()
        board.initialize(state)
        algo = MinMaxAdaptative()
        m = algo.move_select(board, CheckersBoard.WHITE)
        self.assertIsNotNone(m)
