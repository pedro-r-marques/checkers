# distutils: language = c++

from checkers.py_checkers cimport CheckersBoard

cdef extern from "scorer.cc":
    pass

cdef extern from "scorer.h":
    cdef cppclass Scorer:
        Scorer() except +
        int score(const CheckersBoard& board, CheckersBoard.Player player)