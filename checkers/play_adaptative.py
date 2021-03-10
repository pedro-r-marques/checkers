import heapq
from typing import Any, List, Tuple
import random

from .checkers_lib import PyCheckersBoard as CheckersBoard
from .play_minmax import board_score


class MinMaxNode(object):
    __slots__ = [
        'priority', 'generation', 'board', 'move', 'player', 'score', 'heapq']

    def __init__(self, board, move, player):
        self.generation = 0
        self.board = CheckersBoard.copy(board)
        self.board.move(move)
        self.move = move
        self.player = player
        self.score = board_score(self.board, player)
        self.priority = -self.score
        self.heapq = []

    def __lt__(self, rhs):
        return self.priority < rhs.priority


def make_key(board, move, player):
    value = (hash(board), hash(tuple(move)), hash(player))
    return hash(value)


def node_locate(cache, board, move, player, stats):
    if cache is None:
        node = MinMaxNode(board, move, player)
        stats['nodes'] += 1
        return node

    key = make_key(board, move, player)
    if key in cache:
        node = cache[key]
        stats['cached'] += 1
        return node
    node = MinMaxNode(board, move, player)
    stats['nodes'] += 1

    cache[key] = node
    return node


def tree_build(cache, board, player, stats):
    pq = []
    moves = board.valid_moves(player)
    stats['inodes'] += 1
    for mv in moves:
        node = node_locate(cache, board, mv, player, stats)
        heapq.heappush(pq, node)

    return pq


def tree_expand(cache, pq, player, stats):
    opponent = CheckersBoard.WHITE if player == CheckersBoard.BLACK \
        else CheckersBoard.BLACK

    nqueue = []
    for node in pq:
        node.heapq = tree_build(cache, node.board, opponent, stats)
        if node.heapq:
            node.priority = node.score + node.heapq[0].score
        heapq.heappush(nqueue, node)
    return nqueue


def leaf_update(cache, node, stats):
    player = node.player
    opponent = CheckersBoard.WHITE if player == CheckersBoard.BLACK \
        else CheckersBoard.BLACK
    node.heapq = tree_build(cache, node.board, opponent, stats)
    if node.heapq:
        node.priority = node.score + node.heapq[0].score


def tree_updater(cache, pq, update_fn, generation, stats,
                 threshold=100, breath_max=None, depth=0):
    if not pq:
        return []
    pq = pq[:]

    if depth > 8:
        print(pq)
        assert False

    top_p = pq[0].priority

    nq = []
    while pq:
        node = heapq.heappop(pq)
        if node.priority - top_p >= threshold:
            break
        if node.generation == generation:
            heapq.heappush(nq, node)
            continue
        if not node.heapq:
            update_fn(cache, node, stats)
            heapq.heappush(nq, node)
            node.generation = generation
            continue

        node.heapq = tree_updater(cache, node.heapq, update_fn, generation,
                                  stats, threshold=threshold,
                                  breath_max=breath_max, depth=depth+1)
        node.priority = -(node.score + node.heapq[0].priority)
        heapq.heappush(nq, node)
        node.generation = generation
        if breath_max and len(nq) >= breath_max:
            break

    return nq


class MinMaxAdaptative(object):
    def __init__(self, max_depth=6):
        self.n_turns = max_depth - 2
        assert self.n_turns > 0
        self.node_limit = 4 * 1024

    def move_select(self, board, player, turn=None):
        stats = {
            'inodes': 0,
            'nodes': 0,
            'cached': 0,
        }

        counts = board.piece_count()
        if any(x > 0 for x in counts[2:]):
            threshold = 200
        else:
            threshold = 20

        pq = tree_build(None, board, player, stats)
        if not pq:
            return None
        pq = tree_expand(None, pq, player, stats)

        for i in range(self.n_turns):
            cache = {}
            pq = tree_updater(cache, pq, leaf_update, i + 1, stats,
                              threshold=threshold)
            if i >= 2 and stats['nodes'] >= self.node_limit:
                # print(turn, i, stats)
                break

        moves = ([x.move for x in pq if x.priority == pq[0].priority])
        return random.choice(moves)
