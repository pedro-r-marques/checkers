import unittest
import tempfile
import shutil
import os

from .logger import GameLogger, SummaryLogger
from .py_checkers import PyCheckersBoard as CheckersBoard
from .play_random import move_select


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


def log_mock_game(filename):
    logger = GameLogger()
    board = CheckersBoard()
    for turn in range(64):
        player = CheckersBoard.BLACK if turn % 2 == 0 else CheckersBoard.WHITE
        mv = move_select(board, player, turn)
        logger.log(board, turn, player, mv)
        if mv is not None:
            board.move(mv)
        if any(x == 0 for x in board.count()):
            break

    logger.save(filename)


class SummaryLoggerTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_aggregate(self):
        for filename in ['a.dat', 'b.dat']:
            log_mock_game(os.path.join(self.tmpdir, filename))
        summary = SummaryLogger()
        summary.from_directory(self.tmpdir, r'.*\.dat')
        summary.save(os.path.join(self.tmpdir, 'summary.tsv'), 0)
