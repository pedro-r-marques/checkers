import argparse
import random

import tqdm

from .checkers_lib import PyCheckersBoard as CheckersBoard
from .play_minmax import MinMaxPlayer
from .logger import GameLogger, SummaryLogger


def play_game(w_player_fn, b_player_fn):
    board = CheckersBoard()
    turn = 0

    logger = GameLogger()
    winner = 0
    while turn < 128:
        m1 = b_player_fn(board, CheckersBoard.BLACK, turn)
        logger.log(board, turn, CheckersBoard.BLACK, m1)
        if m1 is not None:
            board.move(m1)
        if board.count()[0] == 0:
            winner = CheckersBoard.BLACK
            break
        m2 = w_player_fn(board, CheckersBoard.WHITE, turn)
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

    w_player = MinMaxPlayer()
    b_player = MinMaxPlayer()

    logger = SummaryLogger()
    counts = [0, 0]
    for _ in tqdm.tqdm(range(args.count)):
        w, game_log, turns = play_game(
            w_player.move_select, b_player.move_select)
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
