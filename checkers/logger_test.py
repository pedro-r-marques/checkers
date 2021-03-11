import unittest
import tempfile

from .logger import GameLogger
from .py_checkers import PyCheckersBoard as CheckersBoard


class GameLoggerTest(unittest.TestCase):
    def test_save_load(self):
        logger = GameLogger()
        board = CheckersBoard()
        logger.log(board, 0, CheckersBoard.BLACK, [(5, 0), (4, 1)])
        logger.log(board, 1, CheckersBoard.WHITE, [(2, 1), (3, 0)])
        filename = tempfile.mktemp()
        logger.save(filename)

        reader = GameLogger()
        reader.load(filename)
        self.assertEqual(len(reader.history), 2)
