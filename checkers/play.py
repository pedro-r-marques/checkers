import argparse
import random
import time

import tqdm

from .checkers_lib import PyCheckersBoard as CheckersBoard
from .play_minmax import MinMaxPlayer
from .play_adaptative import MinMaxAdaptative
from .logger import GameLogger, SummaryLogger


def play_game(fn_a, fn_b, runaway_trace=0):
    board = CheckersBoard()
    turn = 0

    def trace_fn(fn, *args):
        start = time.time()
        result = fn(*args)
        elapsed = time.time() - start
        if runaway_trace and elapsed > runaway_trace:
            board, player, turn = args
            print(elapsed, turn, player, board.pieces())
        return result

    logger = GameLogger()
    winner = 0
    while turn < 128:
        m1 = trace_fn(fn_a, board, CheckersBoard.BLACK, turn)
        logger.log(board, turn, CheckersBoard.BLACK, m1)
        if m1 is not None:
            board.move(m1)
        if board.count()[0] == 0:
            winner = CheckersBoard.BLACK
            break
        m2 = trace_fn(fn_b, board, CheckersBoard.WHITE, turn)
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

    w_player = MinMaxPlayer(max_depth=4, select_best=True)
    b_player = MinMaxAdaptative()

    logger = SummaryLogger()
    counts = [0, 0]
    for _ in tqdm.tqdm(range(args.count)):
        w, game_log, turns = play_game(
            w_player.move_select, b_player.move_select, runaway_trace=0.5)
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
