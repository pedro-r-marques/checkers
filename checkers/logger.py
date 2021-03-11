import collections
import pickle


LogEntry = collections.namedtuple(
    'LogEntry', ['board', 'turn', 'player', 'move'])


class GameLogger():
    def __init__(self):
        self.history = collections.deque()

    def log(self, board, turn, player, move):
        self.history.append(LogEntry(board.board(), turn, player, move))

    def save(self, filename):
        with open(filename, 'wb') as fp:
            pickle.dump(self.history, fp)

    def load(self, filename):
        with open(filename, 'rb') as fp:
            self.history = pickle.load(fp)


class SummaryLogger():
    def __init__(self):
        self.data = {}

    @classmethod
    def hash(cls, log_entry):
        board_arr, _, player, _ = log_entry
        return hash((board_arr, player))

    def add(self, game_log, winner, turns):
        for log_entry in game_log.history:
            board_arr, turn, player, move = log_entry
            turn_distance = turns - turn
            h = self.hash(log_entry)
            if h not in self.data:
                results = [(move, [(winner, turn_distance)])]
                self.data[h] = (board_arr, player, results)
                continue
            current = self.data[h]
            if current[0] != board_arr or current[1] != player:
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
