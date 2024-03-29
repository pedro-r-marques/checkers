import argparse
import functools
import datetime
import multiprocessing
import os
import tempfile

import tqdm

from .play import play_game
from .play_minmax import MinMaxPlayer
from .play_probability import StatsPlayer

# Create the stats player once since it loads stats data into memory.
gbl_stats_player = None


def worker(log_dir, game_id):
    global gbl_stats_player
    if gbl_stats_player is None:
        gbl_stats_player = StatsPlayer()

    if game_id & 0x1 == 0:
        w_player = MinMaxPlayer()
        b_player = gbl_stats_player
    else:
        w_player = gbl_stats_player
        b_player = MinMaxPlayer()

    tstamp = datetime.datetime.now()
    w, game_log = play_game(w_player.move_select, b_player.move_select)
    filename = tstamp.strftime("%Y%m%d%H%M%S%f") + ".dat"
    game_log.save(os.path.join(log_dir, filename))
    return w


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--count', type=int, default=100000)
    parser.add_argument(
        '--log-dir', default="",
        help="Directory to which to save the game logs")
    args = parser.parse_args()

    if not args.log_dir:
        args.log_dir = tempfile.mkdtemp()
        print('Logging to', args.log_dir)

    counts = [0, 0, 0]

    worker_fn = functools.partial(worker, args.log_dir)

    with multiprocessing.Pool(processes=args.workers) as pool:
        for result in tqdm.tqdm(
                pool.imap_unordered(worker_fn, range(args.count))):
            w = result
            counts[w] += 1

    print('Results', counts)


if __name__ == '__main__':
    main()
