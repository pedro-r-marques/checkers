import os
import unittest

import urllib3

from .py_checkers import PyCheckersBoard as CheckersBoard
from .play_scorer_tfserv import TFScorerPlayer


def board_from_pieces(pieces):
    state = [[0] * 8 for _ in range(8)]
    for row, col, piece in pieces:
        state[row][col] = piece
    board = CheckersBoard()
    board.initialize(state)
    return board


def tfserving_available():
    http = urllib3.PoolManager()
    try:
        r = http.request(
            'GET', 'http://localhost:8501/v1/models/score_model/metadata')
        return r.status == 200
    except Exception:
        return False


@unittest.skipUnless(
    tfserving_available(), "tfserving not available")
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

    def test_trace(self):
        pieces = [
            [0, 1, 1], [1, 0, 1], [1, 4, 1], [2, 1, 1],
            [3, 2, 2], [4, 3, 2], [4, 5, 1], [4, 7, 1],
            [6, 3, 2], [6, 5, 2], [6, 7, 2], [7, 0, 2]
        ]
        board = board_from_pieces(pieces)
        self.algorithm.move_select(board, CheckersBoard.WHITE, None)
        info = self.algorithm.move_info(board, CheckersBoard.WHITE, None)
        for minfo in info:
            trace = minfo['trace']
            piece = board.get_position(trace[0][0])
            self.assertIn(piece, [CheckersBoard.BLACK,
                          CheckersBoard.BLACK_KING],
                          msg="%r %r" % (minfo['move'], trace))

    def test_multiple_best(self):
        pieces = [
            [0, 1, 4], [0, 3, 3], [1, 6, 2], [4, 1, 4], [7, 0, 2]
        ]
        board = board_from_pieces(pieces)
        info = self.algorithm.move_info(board, CheckersBoard.WHITE, None)
        self.assertTrue(info)
        max_score = info[0]['score']
        moves = [minfo['move']
                 for minfo in info if minfo['score'] == max_score]
        self.assertIn([(0, 3), (4, 7)], moves)
