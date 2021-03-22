"""
"""
import argparse
import pickle
import os

from scipy.stats import multinomial

from .logger import SummaryLogger
from .play_probability import PositionStats, MoveStats


def make_position_stats(gbl_probabilities, move_info, p_threshold=0.2):
    move_data = []
    pos_counts = [0] * 3
    for move, results in move_info:
        counts = [0] * 3
        for result in results:
            counts[result[0]] += 1
            pos_counts[result[0]] += 1
        move_data.append((move, counts))

    total = sum(pos_counts)
    pos_rv = multinomial(total, gbl_probabilities)
    pos_probabilities = [x/total for x in pos_counts]

    moves = []
    p_min = 1.0
    for move, counts in move_data:
        m_sum = sum(counts)
        mv_rv = multinomial(m_sum, pos_probabilities)
        p_value = mv_rv.pmf(counts)
        p_min = min(p_min, p_value)
        mp = [x/m_sum for x in counts]
        move = MoveStats(
            move=move, pmf=p_value, probabilities=mp, counts=counts)
        moves.append(move)

    if p_min >= p_threshold:
        return None

    return PositionStats(
        pmf=pos_rv.pmf(pos_counts),
        probabilities=pos_probabilities,
        moves=moves)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=".")
    parser.add_argument("directories", nargs="+")
    args = parser.parse_args()

    summary = SummaryLogger()
    for dirname in args.directories:
        summary.from_directory(dirname, r'.*\.dat')

    r_sum = sum(summary.results)
    gbl_probabilities = [x/r_sum for x in summary.results]

    player1_positions = {}
    player2_positions = {}

    for entry in summary.data.values():
        board_bytes, player, move_info = entry
        if len(move_info) == 1:
            continue

        pos_stats = make_position_stats(gbl_probabilities, move_info)
        if pos_stats is None:
            continue

        player_data = player1_positions if player == 1 else player2_positions
        player_data[board_bytes] = pos_stats

    filename = os.path.join(args.output_dir, "player1_positions.bin")
    with open(filename, "wb") as fp:
        pickle.dump(player1_positions, fp)

    filename = os.path.join(args.output_dir, "player2_positions.bin")
    with open(filename, "wb") as fp:
        pickle.dump(player2_positions, fp)


if __name__ == "__main__":
    main()
