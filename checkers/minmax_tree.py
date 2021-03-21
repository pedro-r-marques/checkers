import abc
import heapq

import cachetools

from .py_checkers import PyCheckersBoard as CheckersBoard


class MinMaxNode(object):
    """ Node in minmax tree.
    """

    __slots__ = ['board', 'player', 'n_children',
                 'score', 'heapq', 'parents', 'path']

    def __init__(self, board, player):
        self.board = board
        self.player = player    # next player to move
        self.n_children = 0
        self.score = None
        self.heapq = []
        self.parents = []
        self.path = []


class HeapQueueEntry(object):
    __slots__ = ['move', 'score', 'path']

    def __init__(self, move, score, path):
        self.move = move
        self.score = score
        self.path = path

    def __lt__(self, rhs):
        return self.score > rhs.score


class ScorerExecutor(object):
    def __init__(self):
        self.node_update_cb = None

    def set_node_update_cb(self, node_update_cb):
        self.node_update_cb = node_update_cb

    @abc.abstractmethod
    def enqueue(self, node, board, move, player):
        raise NotImplementedError()

    def update(self, node, move, score):
        heapq.heappush(node.heapq, HeapQueueEntry(move, score, [move]))

        if len(node.heapq) == node.n_children:
            qhead = node.heapq[0]
            node.score = qhead.score
            node.path = qhead.path
            self.node_update_cb(node, qhead.path)


class MinMaxTreeExecutor(object):
    def __init__(self, executor, max_depth=4):
        self.max_depth = max_depth
        self.exec = executor
        self.cache = cachetools.Cache(maxsize=32*1024)
        executor.set_node_update_cb(self._node_update)

    def _node_update_parents(self, node, path):
        update_list = []
        for parent, move in node.parents:
            heapq.heappush(parent.heapq, HeapQueueEntry(
                move, -node.score, path))
            node.heapq = []

            if len(parent.heapq) == parent.n_children:
                qhead = parent.heapq[0]
                parent.score = qhead.score
                npath = [qhead.move] + qhead.path
                parent.path = npath
                update_list.append((parent, npath))
        return update_list

    def _node_update(self, node, path):
        work_list = [(node, path)]
        while work_list:
            nwork_list = []
            for wnode, wpath in work_list:
                nwork_list.extend(self._node_update_parents(wnode, wpath))
            work_list = nwork_list

    def _run_minmax(self, node, depth):
        board = node.board
        moves = board.valid_moves(node.player)
        node.n_children = len(moves)
        if not moves:
            node.n_children = 1
            self.exec.enqueue(node, board, None, node.player)

        if depth == 0:
            for move in moves:
                nboard = CheckersBoard.copy(board)
                nboard.move(move)
                self.exec.enqueue(node, nboard, move, node.player)
            return

        opponent = CheckersBoard.WHITE if node.player == CheckersBoard.BLACK \
            else CheckersBoard.BLACK

        children = []
        for move in moves:
            nboard = CheckersBoard.copy(board)
            nboard.move(move)
            key = (hash(nboard), opponent, depth)
            if key in self.cache:
                child = self.cache[key]
                assert child.board == nboard
                if child.score is not None:
                    heapq.heappush(node.heapq, HeapQueueEntry(
                        move, -child.score, child.path))
                    continue
                child.parents.append((node, move))
                continue

            child = MinMaxNode(nboard, opponent)
            self.cache[key] = child
            child.parents.append((node, move))
            children.append(child)

        if len(node.heapq) == node.n_children:
            qhead = node.heapq[0]
            node.score = qhead.score
            self._node_update(node, qhead.path)
            return

        for child in children:
            self._run_minmax(child, depth - 1)

    def move_minmax(self, board, player):
        top_level = MinMaxNode(board, player)
        self._run_minmax(top_level, self.max_depth)
        self.exec.flush()

        if not top_level.heapq:
            return []

        qhead = top_level.heapq[0]
        score = qhead.score
        moves = [m.move for m in top_level.heapq if m.score == score]
        return moves

    def move_info(self, board, player, turn):
        top_level = MinMaxNode(board, player)
        self._run_minmax(top_level, self.max_depth)
        self.exec.flush()

        pq = top_level.heapq

        result = []

        while pq:
            node = heapq.heappop(pq)
            info = {
                'move': node.move,
                'score': float(node.score),
                'trace': node.path,
            }
            result.append(info)

        return result
