import random
import unittest

from .checkers_lib import PyCheckersBoard as CheckersBoard
from .play_minmax import board_score, move_select


class TestMinMax(unittest.TestCase):
    def setUp(self):
        random.seed(1337)

    def test_select_capture(self):
        state = [[0] * 8 for _ in range(8)]
        state[0][5] = CheckersBoard.WHITE
        state[3][4] = CheckersBoard.WHITE
        state[4][3] = CheckersBoard.BLACK
        state[4][1] = CheckersBoard.BLACK

        board = CheckersBoard()
        board.initialize(state)
        m = move_select(board, CheckersBoard.BLACK)
        self.assertEqual(m, [(4, 3), (2, 5)])

    def test_init_board(self):
        board = CheckersBoard()
        self.assertEqual(board_score(board, CheckersBoard.WHITE),
                         board_score(board, CheckersBoard.BLACK))
        board.move([(5, 0), (4, 1)])
        board.move([(2, 7), (3, 6)])
        m = move_select(board, CheckersBoard.BLACK)
        self.assertTrue(m is not None)


if __name__ == '__main__':
    unittest.main()
