import collections
import pickle
import os
import re
import warnings

from libcheckers.py_checkers import PyCheckersBoard as CheckersBoard

LogEntry = collections.namedtuple(
    'LogEntry', ['board', 'turn', 'player', 'move'])


class GameLogger():
    def __init__(self):
        self.history = collections.deque()

    def log(self, board, turn, player, move):
        self.history.append(LogEntry(board.board(), turn, player, move))

    def save(self, filename):
        with open(filename, 'wb') as fp:
            pickle.dump(self.history, fp)

    def load(self, filename):
        with open(filename, 'rb') as fp:
            self.history = pickle.load(fp)

    @staticmethod
    def _board_object(log_entry):
        board = CheckersBoard()
        board.from_byte_array(log_entry.board)
        return board

    def player_counts(self, index):
        """ Return the number of pieces per player after turn X.
        """
        log_entry = self.history[index]
        board = self._board_object(log_entry)
        if log_entry.move is not None:
            board.move(log_entry.move)
        return board.count()


class SummaryLogger():
    def __init__(self):
        self.data = {}
        self.results = [0] * 3

    @classmethod
    def hash(cls, log_entry):
        return hash((log_entry.board, log_entry.player))

    def add(self, game_log, winner):
        turns = len(game_log.history)

        for log_entry in game_log.history:
            turn_distance = turns - log_entry.turn
            h = self.hash(log_entry)
            if h not in self.data:
                results = [(log_entry.move, [(winner, turn_distance)])]
                self.data[h] = (log_entry.board, log_entry.player, results)
                continue
            current = self.data[h]
            if current[0] != log_entry.board or current[1] != log_entry.player:
                warnings.warn('hash collision')
                continue

            exists = False
            for entry in current[2]:
                if entry[0] == log_entry.move:
                    entry[1].append((winner, turn_distance))
                    exists = True
                    break
            if not exists:
                current[2].append((log_entry.move, [(winner, turn_distance)]))

    def from_directory(self, dirname, pattern=None, min_turns=48):
        filenames = os.listdir(dirname)
        if pattern is not None:
            re_pattern = re.compile(pattern)
            filenames = [f for f in filenames if re_pattern.match(f)]
        for basename in filenames:
            log = GameLogger()
            log.load(os.path.join(dirname, basename))
            counts = log.player_counts(-1)
            winner = 0
            if counts[0] == 0:
                winner = CheckersBoard.BLACK
            elif counts[1] == 0:
                winner = CheckersBoard.WHITE
            if winner == 0 and len(log.history) < min_turns:
                continue
            self.results[winner] += 1
            self.add(log, winner)

    def save(self, filename, threshold):
        with open(filename, 'w') as fp:
            for entry in self.data.values():
                pieces, player, move_info = entry
                move_data = []
                count = 0
                for move, results in move_info:
                    counts = [0, 0, 0]
                    for result in results:
                        counts[result[0]] += 1
                    move_data.append((move, counts))
                    count += sum(counts)
                if count < threshold:
                    continue
                line = '\t'.join([str(pieces), str(player), str(move_data)])
                fp.write(line + '\n')
