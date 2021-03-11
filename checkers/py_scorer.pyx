# distutils: language = c++

from checkers.py_scorer cimport Scorer
from checkers.py_checkers cimport PyCheckersBoard, CheckersBoard

cdef class PyScorer:
    cdef Scorer c_impl

    def score(self, PyCheckersBoard board, CheckersBoard.Player player):
        cdef const CheckersBoard* c_board = <CheckersBoard *> &board.c_impl
        return self.c_impl.score(c_board[0], player)