# distutils: language = c++

from checkers.py_scorer cimport Scorer
from checkers.py_checkers cimport PyCheckersBoard, CheckersBoard

cdef class PyScorer:
    cdef Scorer c_impl

    def __cinit__(self, dict params=None):
        cdef Scorer.Params cparams

        if params is not None:
            cparams.piece_value = params['piece_value']
            cparams.king_value = params['king_value']
            cparams.piece_1away_value = params['piece_1away_value']
            cparams.piece_naway_value = params['piece_naway_value']
            self.c_impl = Scorer(cparams)

    def score(self, PyCheckersBoard board, CheckersBoard.Player player):
        cdef const CheckersBoard* c_board = <CheckersBoard *> &board.c_impl
        return self.c_impl.score(c_board[0], player)