import collections
import hashlib
import pickle


class GameLogger():
    def __init__(self):
        self.history = collections.deque()

    def log(self, board, turn, player, move):
        self.history.append((board.board(), turn, player, move))

    def save(self, filename):
        with open(filename, 'wb') as fp:
            pickle.dump(self.history, fp)


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
            pieces, turn, player, move = log_entry
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
