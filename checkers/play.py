import argparse
import collections
import hashlib
import random

import tqdm

from .checkers_lib import PyCheckersBoard as CheckersBoard
from .play_random import move_select as play_random
from .play_minmax import move_select as play_minmax


class GameLogger():
    def __init__(self):
        self.history = collections.deque()

    def log(self, board, turn, player, move):
        self.history.append((board.pieces(), player, move, turn))


class SummaryLogger():
    def __init__(self):
        self.data = {}

    @staticmethod
    def log_hash(log_entry):
        pieces, player, _, _ = log_entry
        h = hashlib.md5()
        h.update(bytes(player))
        for piece in pieces:
            h.update(bytes(piece))
        return h.digest()

    def add(self, game_log, winner, turns):
        for log_entry in game_log.history:
            pieces, player, move, turn = log_entry
            turn_distance = turns - turn
            h = self.log_hash(log_entry)
            if h not in self.data:
                results = [(move, [(winner, turn_distance)])]
                self.data[h] = (pieces, player, results)
                continue
            current = self.data[h]
            if current[0] != pieces or current[1] != player:
                print('hash collision')
                continue

            exists = False
            for entry in current[2]:
                if entry[0] == move:
                    entry[1].append((winner, turn_distance))
                    exists = True
                    break
            if not exists:
                current[2].append((move, [(winner, turn_distance)]))

    def save(self, filename, threshold):
        with open(filename, 'w') as fp:
            for entry in self.data.values():
                pieces, player, move_info = entry
                move_data = []
                count = 0
                for move, results in move_info:
                    counts = [0, 0]
                    for result in results:
                        counts[result[0] - 1] += 1
                    move_data.append((move, counts))
                    count += sum(counts)
                if count < threshold:
                    continue
                line = '\t'.join([str(pieces), str(player), str(move_data)])
                fp.write(line + '\n')


def play_game(fn_a, fn_b):
    board = CheckersBoard()
    turn = 0

    logger = GameLogger()
    winner = 0
    while turn < 1024:
        m1 = fn_a(board, CheckersBoard.BLACK, turn)
        logger.log(board, turn, CheckersBoard.BLACK, m1)
        if m1 is not None:
            board.move(m1)
        if board.count()[0] == 0:
            winner = CheckersBoard.BLACK
            break
        m2 = fn_b(board, CheckersBoard.WHITE, turn)
        logger.log(board, turn, CheckersBoard.WHITE, m2)
        if m2 is not None:
            board.move(m2)
        if board.count()[1] == 0:
            winner = CheckersBoard.WHITE
            break
        turn += 1

    return winner, logger, turn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--count', type=int, default=10,
        help="Number of games to play")
    parser.add_argument(
        '--save-log', action="store_true",
        help="Save the summary of the played turns and outcomes")
    parser.add_argument(
        '--save-threshold', type=int, default=10,
        help="Threshold for log saving.")
    args = parser.parse_args()

    logger = SummaryLogger()
    counts = [0, 0]
    for _ in tqdm.tqdm(range(args.count)):
        w, game_log, turns = play_game(play_minmax, play_minmax)
        if w == 0:
            continue
        logger.add(game_log, w, turns)
        counts[w - 1] += 1
    print('Wins', counts)
    if args.save_log:
        logger.save('play.log', args.save_threshold)


if __name__ == '__main__':
    random.seed(1337)
    main()
