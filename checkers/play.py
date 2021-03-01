import random

from .checkers import CheckersBoard


def make_play(board, player):
    moves = board.valid_moves(player)
    move = random.choice(moves)
    return move
