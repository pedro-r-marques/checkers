# distutils: language = c++

from libcpp.utility cimport pair
from libcpp.list cimport list as cpplist
from libcpp.vector cimport vector

cdef extern from "<array>" namespace "std" nogil:
    cdef cppclass array4 "std::array<int, 4>":
        array4() except+
        int& operator[](size_t)

cdef extern from "checkers.cc":
    pass

cdef extern from "checkers.h":
    cdef cppclass CheckersBoard:
        enum Player:
            WHITE = 1
            BLACK = 2

        enum Piece:
            WHITE_PAWN = 1
            BLACK_PAWN = 2
            WHITE_KING = 3
            BLACK_KING = 4

        ctypedef pair[int, int] Position
        ctypedef vector[Position] Move

        CheckersBoard() except +
        CheckersBoard(CheckersBoard&) except +
        CheckersBoard(const vector[int]&) except +

        void initialize(const vector[int]&)
    
        bint operator==(CheckersBoard&, CheckersBoard&)
        unsigned long long hash()

        pair[int, int] count()
        array4 piece_count()

        cpplist[Move] valid_moves(Player)

        pair[cpplist[Move], cpplist[Move]] position_moves(Position)
        
        Piece get_position(Position)

        cpplist[vector[unsigned char]] pieces()
        const char* data()

        void move(const Move&)

cdef class PyCheckersBoard:
    cdef CheckersBoard c_impl
