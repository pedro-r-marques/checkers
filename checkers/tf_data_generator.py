import os
import random
import re

import tensorflow as tf
import numpy as np

from checkers.logger import GameLogger
from libcheckers.py_checkers import PyCheckersBoard


class DataGenerator(tf.keras.utils.Sequence):
    re_pattern = re.compile(r'.*\.dat')

    def __init__(self, datadirs, n_sample_files=None, batch_size=64,
                 samples_per_file=8):
        self.datadirs = datadirs
        self.filenames = []
        self.n_sample_files = n_sample_files
        self.batch_size = batch_size
        self.samples_per_file = samples_per_file
        self._listdirs()

    def __len__(self):
        n_files = len(self.filenames)
        if self.n_sample_files is not None:
            n_files = min(n_files, self.n_sample_files)
        n_samples = n_files * self.samples_per_file
        return (n_samples + self.batch_size - 1) // self.batch_size

    def _listdirs(self):
        for dirname in self.datadirs:
            filenames = os.listdir(dirname)
            filenames = [os.path.join(dirname, f) for f in filenames
                         if self.re_pattern.match(f)]
            self.filenames.extend(filenames)

    def _prediction_score(self, entry, n_turns):
        x = entry.turn / (n_turns - 1) * 80
        return 2.0 * 1/(1 + np.exp((80 - x) * .08))

    def _entry_extract(self, entry, n_turns, winner, x_data, y_data):
        board = PyCheckersBoard()
        board.from_byte_array(entry.board)
        if entry.move is not None:
            board.move(entry.move)
        x_board = np.zeros((8, 4, 4), dtype=bool)
        for piece in board.pieces():
            row = piece[0]
            col = piece[1] // 2
            x_board[row][col][piece[2] - 1] = True

        x_player = np.zeros((2,), dtype=bool)
        x_player[entry.player - 1] = True

        x_data[0].append(x_board)
        x_data[1].append(x_player)

        y_out = np.zeros((3,), dtype=np.float32)
        y_out[winner] = self._prediction_score(entry, n_turns)
        y_data.append(y_out)

    @staticmethod
    def _log_winner(log):
        counts = log.player_counts(-1)
        winner = 0
        if counts[0] == 0:
            winner = 2
        elif counts[1] == 0:
            winner = 1
        return winner

    def _log_extract(self, filename, x_data, y_data):
        log = GameLogger()
        log.load(filename)
        winner = self._log_winner(log)
        indices = list(range(len(log.history)))
        random.shuffle(indices)
        indices = indices[:self.samples_per_file]
        entries = [log.history[i] for i in indices]
        n_turns = log.history[-1].turn + 1
        for entry in entries:
            self._entry_extract(entry, n_turns, winner, x_data, y_data)

    def _log_extract_all(self, filename, x_data, y_data):
        log = GameLogger()
        log.load(filename)
        winner = self._log_winner(log)
        n_turns = log.history[-1].turn + 1
        for entry in log.history:
            self._entry_extract(entry, n_turns, winner, x_data, y_data)

    def __getitem__(self, index):
        files_per_batch = self.batch_size // self.samples_per_file
        start = index * files_per_batch

        x_data = [[], []]
        y_data = []
        for i in range(files_per_batch):
            if start + i == len(self.filenames):
                break
            filename = self.filenames[start + i]
            self._log_extract(filename, x_data, y_data)

        return [np.stack(x) for x in x_data], np.stack(y_data)

    def on_epoch_end(self):
        random.shuffle(self.filenames)
