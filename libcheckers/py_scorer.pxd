# distutils: language = c++

from .py_checkers cimport CheckersBoard

cdef extern from "scorer.cc":
    pass

cdef extern from "scorer.h":
    cdef cppclass Scorer:
        struct Params:
            int piece_value
            int king_value
            int piece_1away_value
            int piece_naway_value

        Scorer() except +
        Scorer(const Params&) except +
        int score(const CheckersBoard& board, CheckersBoard.Player player)