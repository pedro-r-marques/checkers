"""
"""
import functools
import random

from .checkers import CheckersBoard
from .play_random import move_select as random_select

SCORE_MIN = -1000
SCORE_MAX = 1000


def board_score(board, player):
    counts = board.piece_count()
    if player == CheckersBoard.WHITE:
        player_count = (counts[CheckersBoard.WHITE - 1] +
                        counts[CheckersBoard.WHITE_KING - 1])
        opponent_count = (counts[CheckersBoard.BLACK - 1] +
                          counts[CheckersBoard.BLACK_KING - 1])
    elif player == CheckersBoard.BLACK:
        player_count = (counts[CheckersBoard.BLACK - 1] +
                        counts[CheckersBoard.BLACK_KING - 1])
        opponent_count = (counts[CheckersBoard.WHITE - 1] +
                          counts[CheckersBoard.WHITE_KING - 1])
    else:
        raise ValueError('Invalid player id')

    if player_count == 0:
        return SCORE_MIN
    if opponent_count == 0:
        return SCORE_MAX

    score = 0

    king_delta = (counts[CheckersBoard.WHITE_KING - 1] -
                  counts[CheckersBoard.BLACK_KING - 1])
    piece_delta = (counts[CheckersBoard.WHITE - 1] -
                   counts[CheckersBoard.BLACK - 1])

    if player == CheckersBoard.BLACK:
        king_delta = -king_delta
        piece_delta = -piece_delta

    score += king_delta * 100
    score += piece_delta * 10

    return score


@functools.lru_cache(maxsize=32*1024)
def move_minmax(board, player, depth, rand=False):
    moves = board.valid_moves(player, select_capture=True)
    if not moves:
        return None, 0
    opponent = CheckersBoard.WHITE if player == CheckersBoard.BLACK \
        else CheckersBoard.BLACK

    scores = []
    deltas = []
    best_delta = SCORE_MIN
    best_index = 0
    for i, move in enumerate(moves):
        nboard = CheckersBoard.copy(board)
        nboard.move(move)
        score = board_score(nboard, player)
        if depth > 0:
            _, opp_score = move_minmax(nboard, opponent, depth - 1)
        else:
            opp_score = 0
        delta = score - opp_score
        scores.append(score)
        deltas.append(delta)
        if delta > best_delta:
            best_delta = delta
            best_index = i

    if rand:
        weights = [x - min(deltas) for x in deltas]
        best_index = random.choices(range(len(moves)), weights=weights)[0]

    move = moves[best_index]
    score = scores[best_index]

    return move, score


def move_select(board, player, turn=None):
    if turn is not None and turn == 0:
        return random_select(board, player, turn)
    m, _ = move_minmax(board, player, 4, rand=True)
    return m
