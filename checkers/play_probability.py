import collections
import os
import pickle
import random

from .play_minmax import MinMaxPlayer

MoveStats = collections.namedtuple(
    'MoveStats', ['move', 'pmf', 'probabilities', 'counts'])
PositionStats = collections.namedtuple(
    'PositionStats', ['pmf', 'probabilities', 'moves'])


class StatsPlayer(object):
    DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    def __init__(self, **kwargs):
        self.player1_positions = {}
        self.player2_positions = {}
        self.min_max_player = MinMaxPlayer(**kwargs)
        self._load_data()

    def _load_data(self):
        filename = os.path.join(self.DATADIR, 'player1_positions.bin')
        with open(filename, 'rb') as fp:
            self.player1_positions = pickle.load(fp)

        filename = os.path.join(self.DATADIR, 'player2_positions.bin')
        with open(filename, 'rb') as fp:
            self.player2_positions = pickle.load(fp)

    def move_info(self, board, player, turn):
        base_info = self.min_max_player.move_info(board, player, turn)
        player_data = self.player1_positions if player == 1 \
            else self.player2_positions
        pos_data = player_data.get(board.board())
        if pos_data is None:
            return base_info

        pos_moves = {tuple(m.move): m for m in pos_data.moves}
        for entry in base_info:
            mv_stats = pos_moves.get(tuple(entry['move']))
            if mv_stats is None:
                continue
            entry['probabilities'] = mv_stats.probabilities
            entry['pmf'] = mv_stats.pmf

        return base_info

    def move_select(self, board, player, turn=None):
        player_data = self.player1_positions if player == 1 \
            else self.player2_positions

        pos_data = player_data.get(board.board())
        if pos_data is None:
            return self.min_max_player.move_select(board, player, turn)

        moves, scores = self.min_max_player.move_scores(board, player, turn)
        best_score = max(scores)
        pos_moves = {tuple(m.move): m for m in pos_data.moves}

        best_moves = []
        best_probability = 0.
        best_index = -1

        for i, s in enumerate(scores):
            if s != best_score:
                continue
            move = moves[i]

            mv_stats = pos_moves.get(tuple(move))
            if mv_stats is not None and mv_stats.pmf < 0.2:
                probability = mv_stats.probabilities[player]
            else:
                probability = 0
            if probability > best_probability:
                best_probability = probability
                best_index = len(best_moves)

            best_moves.append(move)

        if best_index == -1:
            return random.choice(best_moves)
        return best_moves[best_index]
