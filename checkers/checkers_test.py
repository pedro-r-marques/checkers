import unittest

from checkers.checkers import CheckersBoard


class CheckersBoardTest(unittest.TestCase):
    def test_init_count(self):
        board = CheckersBoard()
        self.assertEqual(board.count(), (12, 12))

    def test_init_white_moves(self):
        board = CheckersBoard()
        moves = board.valid_moves(CheckersBoard.WHITE)
        self.assertEqual(len(moves), 7)
        m0 = [end for begin, end in moves if begin == (2, 1)]
        self.assertEqual(m0, [(3, 0), (3, 2)])
        m4 = [end for begin, end in moves if begin == (2, 7)]
        self.assertEqual(m4, [(3, 6)])

    def test_init_black_moves(self):
        board = CheckersBoard()
        moves = board.valid_moves(CheckersBoard.BLACK)
        self.assertEqual(len(moves), 7)
        m0 = [end for begin, end in moves if begin == (5, 0)]
        self.assertEqual(m0, [(4, 1)])
        m4 = [end for begin, end in moves if begin == (5, 6)]
        self.assertEqual(m4, [(4, 5), (4, 7)])

    def test_eat_piece(self):
        state = [[0] * 8 for _ in range(8)]
        state[4][5] = CheckersBoard.WHITE
        state[5][4] = CheckersBoard.BLACK
        board = CheckersBoard(initial_state=state)
        moves = board.valid_moves(CheckersBoard.BLACK)
        self.assertListEqual(moves, [[(5, 4), (4, 3)], [(5, 4), (3, 6)]])

        board.move([(5, 4), (3, 6)])
        self.assertEqual(board.count(), (0, 1))
        self.assertEqual(board.get_position((3, 6)), CheckersBoard.BLACK)

    def test_eat_double(self):
        state = [[0] * 8 for _ in range(8)]
        state[2][5] = CheckersBoard.WHITE
        state[4][5] = CheckersBoard.WHITE
        state[5][4] = CheckersBoard.BLACK
        board = CheckersBoard(initial_state=state)
        moves = board.valid_moves(CheckersBoard.BLACK)
        self.assertEqual(len(moves), 2)
        board.move(moves[1])
        self.assertEqual(board.count(), (0, 1))
        self.assertEqual(board.get_position((1, 4)), CheckersBoard.BLACK)

    def test_eat_border(self):
        state = [[0] * 8 for _ in range(8)]
        state[4][7] = CheckersBoard.WHITE
        state[5][6] = CheckersBoard.BLACK
        board = CheckersBoard(initial_state=state)
        moves = board.valid_moves(CheckersBoard.BLACK)
        self.assertEqual(moves, [[(5, 6), (4, 5)]])

    def test_make_king(self):
        state = [[0] * 8 for _ in range(8)]
        state[1][1] = CheckersBoard.BLACK
        state[6][0] = CheckersBoard.WHITE
        board = CheckersBoard(initial_state=state)
        board.move([(1, 1), (0, 2)])
        self.assertEqual(board.get_position((0, 2)), CheckersBoard.BLACK_KING)
        board.move([(6, 0), (7, 1)])
        self.assertEqual(board.get_position((7, 1)), CheckersBoard.WHITE_KING)

    def test_king_simple_capture_move(self):
        state = [[0] * 8 for _ in range(8)]
        state[0][2] = CheckersBoard.BLACK_KING
        state[3][5] = CheckersBoard.WHITE
        board = CheckersBoard(initial_state=state)
        board.move([(0, 2), (4, 6)])
        self.assertEqual(board.count(), (0, 1))
        self.assertEqual(board.get_position((4, 6)), CheckersBoard.BLACK_KING)

    def test_king_no_capture_move(self):
        state = [[0] * 8 for _ in range(8)]
        state[0][2] = CheckersBoard.BLACK_KING
        state[3][5] = CheckersBoard.WHITE
        board = CheckersBoard(initial_state=state)
        board.move([(0, 2), (2, 0)])
        self.assertEqual(board.count(), (1, 1))
        self.assertEqual(board.get_position((2, 0)), CheckersBoard.BLACK_KING)

    def test_king_multi_capture_move(self):
        state = [[0] * 8 for _ in range(8)]
        state[0][2] = CheckersBoard.BLACK_KING
        state[3][5] = CheckersBoard.WHITE
        state[6][4] = CheckersBoard.WHITE
        state[5][1] = CheckersBoard.WHITE
        board = CheckersBoard(initial_state=state)
        board.move([(0, 2), (4, 6), (7, 3), (4, 0)])
        self.assertEqual(board.count(), (0, 1))
        self.assertEqual(board.get_position((4, 0)), CheckersBoard.BLACK_KING)

    def test_king_capture_move_space(self):
        state = [[0] * 8 for _ in range(8)]
        state[0][2] = CheckersBoard.BLACK_KING
        state[3][5] = CheckersBoard.WHITE
        state[6][4] = CheckersBoard.WHITE
        state[7][3] = CheckersBoard.WHITE
        board = CheckersBoard(initial_state=state)
        board.move([(0, 2), (4, 6)])
        self.assertEqual(board.count(), (2, 1))
        self.assertEqual(board.get_position((4, 6)), CheckersBoard.BLACK_KING)


if __name__ == '__main__':
    unittest.main()
