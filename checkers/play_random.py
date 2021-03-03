import random


def move_select(board, player, turn):
    moves = board.valid_moves(player)
    if not moves:
        return None
    move = random.choice(moves)
    return move
