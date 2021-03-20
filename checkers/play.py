import argparse
import os
import random
import tempfile

import tqdm

from .py_checkers import PyCheckersBoard as CheckersBoard
from .play_minmax import MinMaxPlayer
from .play_probability import StatsPlayer
from .play_scorer_model import TFScorerPlayer
from .logger import GameLogger, SummaryLogger


def play_game(w_player_fn, b_player_fn):
    board = CheckersBoard()

    logger = GameLogger()
    winner = 0

    for turn in range(256):
        if turn % 2 == 0:
            player = CheckersBoard.BLACK
            move_select_fn = b_player_fn
        else:
            player = CheckersBoard.WHITE
            move_select_fn = w_player_fn

        mv = move_select_fn(board, player, turn)
        logger.log(board, turn, player, mv)
        if mv is not None:
            board.move(mv)

        counts = board.count()
        if counts[0] == 0:
            winner = CheckersBoard.BLACK
            break
        if counts[1] == 0:
            winner = CheckersBoard.WHITE
            break

    return winner, logger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--count', type=int, default=10,
        help="Number of games to play")
    parser.add_argument(
        '--log-dir', default="",
        help="Directory to which to save the game logs")
    parser.add_argument(
        '--summary', action='store_true',
        help="Generate a summary from the moves")
    parser.add_argument(
        '--summary-threshold', type=int, default=10,
        help="Threshold for log summary.")
    args = parser.parse_args()

    if not args.log_dir:
        args.log_dir = tempfile.mkdtemp()
        print('Logging to', args.log_dir)

    w_player = TFScorerPlayer()
    b_player = StatsPlayer(select_best=True)

    summary = SummaryLogger()
    counts = [0, 0, 0]
    for i in tqdm.tqdm(range(args.count)):
        w, game_log = play_game(
            w_player.move_select, b_player.move_select)
        game_log.save(os.path.join(args.log_dir, f'{i}.dat'))
        summary.add(game_log, w)
        counts[w] += 1

    print('Results', counts)
    if args.summary:
        summary.save(os.path.join(args.log_dir, 'summary.tsv'),
                     args.summary_threshold)


if __name__ == '__main__':
    random.seed(1337)
    main()
