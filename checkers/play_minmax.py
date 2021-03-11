# distutils: language = c++

"""
"""
import functools
import random

from .py_checkers import PyCheckersBoard as CheckersBoard
from .py_scorer import PyScorer
from .play_random import move_select as random_select

SCORE_MIN = -1000
SCORE_MAX = 1000

scorer = PyScorer()

@functools.lru_cache(maxsize=32*1024)
def move_minmax(board, player, depth):
    moves = board.valid_moves(player)
    if not moves:
        return [], [0], 0
    opponent = CheckersBoard.WHITE if player == CheckersBoard.BLACK \
        else CheckersBoard.BLACK

    scores = []
    best_score = SCORE_MIN
    best_index = 0
    for i, move in enumerate(moves):
        nboard = CheckersBoard.copy(board)
        nboard.move(move)
        score = scorer.score(nboard, player)
        if depth > 0:
            _, opp_scores, ix = move_minmax(nboard, opponent, depth - 1)
            opp_score = opp_scores[ix]
        else:
            opp_score = 0
        score = score - opp_score
        scores.append(score)
        if score > best_score:
            best_score = score
            best_index = i

    return moves, scores, best_index


class MinMaxPlayer(object):
    def __init__(self, max_depth=4, select_best=False):
        self.max_depth = max_depth
        self.select_best = select_best

    def make_weights(self, scores):
        if self.select_best:
            m = max(scores)
            return [1 if v == m else 0 for v in scores]
        return [x - min(scores) + 1 for x in scores]

    def move_info(self, board, player, turn):
        moves, scores, _ = move_minmax(
            board, player, self.max_depth)
        weights = self.make_weights(scores)
        result = []
        for move, score, weight in zip(moves, scores, weights):
            result.append({'move': move, 'score': score, 'weight': weight})
        return result

    def move_select(self, board, player, turn=None):
        if turn is not None and turn == 0:
            return random_select(board, player, turn)
        moves, scores, _ = move_minmax(board, player, self.max_depth)
        if not moves:
            return None
        weights = self.make_weights(scores)
        m = random.choices(moves, weights=weights)
        return m[0]
