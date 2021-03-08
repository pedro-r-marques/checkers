"""
"""
import functools
import random

from .checkers_lib import PyCheckersBoard as CheckersBoard
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
def move_minmax(board, player, depth, rand_move_select=False,
                return_debug_info=False):
    moves = board.valid_moves(player)
    if not moves:
        return None, 0
    opponent = CheckersBoard.WHITE if player == CheckersBoard.BLACK \
        else CheckersBoard.BLACK

    scores = []
    best_score = SCORE_MIN
    best_index = 0
    for i, move in enumerate(moves):
        nboard = CheckersBoard.copy(board)
        nboard.move(move)
        score = board_score(nboard, player)
        if depth > 0:
            _, opp_score = move_minmax(nboard, opponent, depth - 1)
        else:
            opp_score = 0
        score = score - opp_score
        scores.append(score)
        if score > best_score:
            best_score = score
            best_index = i

    def make_weights(scores):
        return [x - min(scores) + 1 for x in scores]

    if return_debug_info:
        return moves, scores, make_weights(scores)

    if rand_move_select:
        weights = make_weights(scores)
        best_index = random.choices(range(len(moves)), weights=weights)[0]

    move = moves[best_index]
    score = scores[best_index]

    return move, score


def play_minimax_debug(board, player, turn):
    moves, scores, weights = move_minmax(
        board, player, 4, return_debug_info=True)
    result = []
    for move, score, weight in zip(moves, scores, weights):
        result.append({'move': move, 'score': score, 'weight': weight})
    return result


def move_select(board, player, turn=None):
    if turn is not None and turn == 0:
        return random_select(board, player, turn)
    m, _ = move_minmax(board, player, 4, rand_move_select=True)
    return m
