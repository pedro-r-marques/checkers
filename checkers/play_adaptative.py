import dataclasses
import heapq
from typing import Any, List, Tuple
import random

from .checkers_lib import PyCheckersBoard as CheckersBoard
from .play_minmax import board_score


@dataclasses.dataclass(order=True)
class MinMaxNode:
    priority: int
    board: CheckersBoard = dataclasses.field(compare=False)
    player: int = dataclasses.field(compare=False)
    move: Tuple[int, int] = dataclasses.field(compare=False)
    score: int = dataclasses.field(compare=False)
    heapq: List[Any] = dataclasses.field(compare=False)

    def __init__(self, board, move, player):
        self.heapq = []
        self.board = CheckersBoard.copy(board)
        self.board.move(move)
        self.player = player
        self.move = move
        self.score = board_score(self.board, player)
        self.priority = -self.score


def tree_build(board, player, stats):
    pq = []
    moves = board.valid_moves(player)
    stats['inodes'] += 1
    for mv in moves:
        node = MinMaxNode(board, mv, player)
        heapq.heappush(pq, node)

    return pq


def tree_expand(pq, player, stats):
    opponent = CheckersBoard.WHITE if player == CheckersBoard.BLACK \
        else CheckersBoard.BLACK

    nqueue = []
    for node in pq:
        node.heapq = tree_build(node.board, opponent, stats)
        if node.heapq:
            node.priority = node.score + node.heapq[0].score
        heapq.heappush(nqueue, node)
    return nqueue


def leaf_update(node, stats):
    player = node.player
    opponent = CheckersBoard.WHITE if player == CheckersBoard.BLACK \
        else CheckersBoard.BLACK
    node.heapq = tree_build(node.board, opponent, stats)
    if node.heapq:
        node.priority = node.score + node.heapq[0].score


def tree_updater(pq, update_fn, stats, threshold=100, breath_max=None):
    if not pq:
        return []
    pq = pq[:]

    top_p = pq[0].priority

    nq = []
    while pq:
        node = heapq.heappop(pq)
        if node.priority - top_p >= threshold:
            break
        if not node.heapq:
            update_fn(node, stats)
            heapq.heappush(nq, node)
            continue

        node.heapq = tree_updater(node.heapq, update_fn, stats)
        node.priority = -(node.score + node.heapq[0].priority)
        heapq.heappush(nq, node)
        if breath_max and len(nq) >= breath_max:
            break

    return nq


class MinMaxAdaptative(object):
    def __init__(self, max_depth=6):
        self.n_turns = max_depth - 2
        assert self.n_turns > 0
        self.inode_limit = 1024

    def move_select(self, board, player, turn=None):
        stats = {
            'inodes': 0,
        }
        pq = tree_build(board, player, stats)
        pq = tree_expand(pq, player, stats)

        for i in range(self.n_turns):
            pq = tree_updater(pq, leaf_update, stats,
                              breath_max=8 if i > 2 else None)
            if stats['inodes'] >= self.inode_limit:
                break

        moves = ([x.move for x in pq if x.priority == pq[0].priority])
        return random.choice(moves)
