# distutils: language = c++

from cpython.bytes cimport PyBytes_FromStringAndSize
from libcpp.vector cimport vector
from .py_checkers import PyCheckersBoard

cdef class PyCheckersBoard:
    WHITE = 1
    BLACK = 2
    WHITE_KING = 3
    BLACK_KING = 4

    BOARD_SIZE = 8

    def __hash__(self):
        return self.c_impl.hash()
    
    def __eq__(self, PyCheckersBoard rhs):
        return self.c_impl == rhs.c_impl

    def initialize(self, state):
        cdef vector[int] flat_vec = [x for row in state for x in row]
        self.c_impl.initialize(flat_vec)

    def from_byte_array(self, byte_arr):
        cdef vector[int] flat_vec = [int(x) for x in byte_arr]
        self.c_impl.initialize(flat_vec)

    def copy(self):
        dst = PyCheckersBoard()
        dst.c_impl = self.c_impl
        return dst

    def count(self):
        return self.c_impl.count()
    
    def piece_count(self):
        arr = self.c_impl.piece_count()
        counts = [0] * 4
        for i in range(4):
            counts[i] = arr[i]
        return counts

    def valid_moves(self, player):
        return self.c_impl.valid_moves(player)

    def position_moves(self, pos):
        if not isinstance(pos, tuple) or len(pos) != 2 or \
                not all(isinstance(x, int) for x in pos):
            raise ValueError('Argument must be a Tuple[int, int]')
        return self.c_impl.position_moves(pos)

    def get_position(self, pos):
        if not isinstance(pos, tuple) or len(pos) != 2 or \
                not all(isinstance(x, int) for x in pos):
            raise ValueError('Argument must be a Tuple[int, int]')
        return self.c_impl.get_position(pos)

    def pieces(self):
        return self.c_impl.pieces()

    def board(self):
        return PyBytes_FromStringAndSize(self.c_impl.data(), 64)

    def move(self, mv):
        return self.c_impl.move(mv)    
