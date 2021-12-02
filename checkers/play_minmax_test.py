import random
import unittest

from libcheckers.py_checkers import PyCheckersBoard as CheckersBoard
from libcheckers.py_scorer import PyScorer
from .play_minmax import MinMaxPlayer


def move_info_best(debug_data):
    if not debug_data:
        return []
    max_score = debug_data[0]['score']
    for entry in debug_data[1:]:
        if entry['score'] > max_score:
            max_score = entry['score']
    best = []
    for entry in debug_data:
        if entry['score'] != max_score:
            continue
        best.append(entry['move'])
    return best


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
        algorithm = MinMaxPlayer()
        m = algorithm.move_select(board, CheckersBoard.BLACK)
        self.assertEqual(m, [(4, 3), (2, 5)])

    def test_init_board(self):
        board = CheckersBoard()
        scorer = PyScorer()
        self.assertEqual(scorer.score(board, CheckersBoard.WHITE),
                         scorer.score(board, CheckersBoard.BLACK))
        board.move([(5, 0), (4, 1)])
        board.move([(2, 7), (3, 6)])
        algorithm = MinMaxPlayer()
        m = algorithm.move_select(board, CheckersBoard.BLACK)
        self.assertTrue(m is not None)

    def test_weights(self):
        state = [
            [0, 1, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 1, 0, 2, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 2, 0, 2],
            [2, 0, 2, 0, 2, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 0, 2],
            [2, 0, 2, 0, 2, 0, 2, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        algorithm = MinMaxPlayer()
        m = algorithm.move_select(board, CheckersBoard.WHITE)
        self.assertIsNotNone(m)

    def test_delay_move(self):
        state = [
            [0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [2, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 2, 0, 0, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        algorithm = MinMaxPlayer()
        result = algorithm.move_info(board, CheckersBoard.WHITE, None)
        self.assertTrue(result)

        best = move_info_best(result)
        self.assertNotIn([((1, 0), (2, 1))], best)

    def test_at_end(self):
        state = [
            [0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 0, 0, 0, 0, 0],
            [0, 0, 2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 2, 0, 0, 0, 0, 0],
        ]
        board = CheckersBoard()
        board.initialize(state)
        algorithm = MinMaxPlayer()
        result = algorithm.move_info(board, CheckersBoard.WHITE, None)
        self.assertTrue(result)
        best = move_info_best(result)
        self.assertNotIn([((4, 1), (6, 3))], best)

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
        algorithm = MinMaxPlayer()
        result = algorithm.move_info(board, CheckersBoard.WHITE, None)
        best = move_info_best(result)
        self.assertNotIn([(5, 2), (6, 3)], best)


if __name__ == '__main__':
    unittest.main()
