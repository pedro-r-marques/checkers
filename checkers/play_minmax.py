# distutils: language = c++

"""
"""
import functools
import random

from libcheckers.py_checkers import PyCheckersBoard as CheckersBoard
from libcheckers.py_scorer import PyScorer
from .play_random import move_select as random_select

SCORE_MIN = -1000
SCORE_MAX = 1000


@functools.lru_cache(maxsize=32*1024)
def move_minmax(scorer, board, player, depth):
    moves = board.valid_moves(player)
    if not moves:
        return [None], [scorer.score(board, player)], 0
    opponent = CheckersBoard.WHITE if player == CheckersBoard.BLACK \
        else CheckersBoard.BLACK

    scores = []
    best_score = SCORE_MIN
    best_index = 0
    for i, move in enumerate(moves):
        nboard = CheckersBoard.copy(board)
        nboard.move(move)
        if depth > 0:
            _, opp_scores, ix = move_minmax(
                scorer, nboard, opponent, depth - 1)
            score = -opp_scores[ix]
        else:
            score = scorer.score(nboard, player)
        scores.append(score)
        if score > best_score:
            best_score = score
            best_index = i

    return moves, scores, best_index


def move_minmax_trace(scorer, board, player, depth):
    moves = board.valid_moves(player)
    if not moves:
        return [None], [scorer.score(board, player)], [[]], 0
    opponent = CheckersBoard.WHITE if player == CheckersBoard.BLACK \
        else CheckersBoard.BLACK

    scores = []
    traces = [[] for _ in range(len(moves))]
    best_score = SCORE_MIN
    best_index = 0
    for i, move in enumerate(moves):
        nboard = CheckersBoard.copy(board)
        nboard.move(move)
        if depth > 0:
            opp_moves, opp_scores, opp_traces, ix = move_minmax_trace(
                scorer, nboard, opponent, depth - 1)
            traces[i] = [(opp_moves[ix], opp_scores[ix])] + opp_traces[ix]
            score = -opp_scores[ix]
        else:
            score = scorer.score(nboard, player)

        scores.append(score)

        if score > best_score:
            best_score = score
            best_index = i

    return moves, scores, traces, best_index


class MinMaxPlayer(object):
    def __init__(self, max_depth=4, select_best=False, scorer_params=None):
        self.max_depth = max_depth
        self.select_best = select_best
        self.scorer = PyScorer(scorer_params)

    def make_weights(self, scores):
        if self.select_best:
            m = max(scores)
            return [1 if v == m else 0 for v in scores]
        return [x - min(scores) + 1 for x in scores]

    def move_info(self, board, player, turn):
        moves, scores, traces, _ = move_minmax_trace(
            self.scorer, board, player, self.max_depth)
        weights = self.make_weights(scores)
        result = []
        for move, score, trace, weight in zip(moves, scores, traces, weights):
            result.append({'move': move, 'score': score,
                           'trace': trace, 'weight': weight})
        return result

    def move_scores(self, board, player, turn=None):
        moves, scores, _ = move_minmax(
            self.scorer, board, player, self.max_depth)
        return moves, scores

    def move_select(self, board, player, turn=None):
        if turn is not None and turn == 0:
            return random_select(board, player, turn)
        moves, scores, _ = move_minmax(
            self.scorer, board, player, self.max_depth)
        if not moves:
            return None
        weights = self.make_weights(scores)
        m = random.choices(moves, weights=weights)
        return m[0]
