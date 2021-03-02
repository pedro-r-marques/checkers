import random

from .checkers import CheckersBoard


def random_play(board, player, turn):
    moves = board.valid_moves(player)
    if not moves:
        return None
    move = random.choice(moves)
    return move


def play_game(fn_a, fn_b):
    board = CheckersBoard()
    turn = 0

    log = []
    winner = 0
    while turn < 1024:
        m1 = fn_a(board, CheckersBoard.BLACK, turn)
        log.append(m1)
        if m1 is not None:
            board.move(m1)
        if board.count()[0] == 0:
            winner = CheckersBoard.BLACK
            break
        m2 = fn_a(board, CheckersBoard.WHITE, turn)
        log.append(m2)
        if m2 is not None:
            board.move(m2)
        if board.count()[1] == 0:
            winner = CheckersBoard.WHITE
            break
        turn += 1

    return winner


def main():
    counts = [0, 0]
    for _ in range(100):
        w = play_game(random_play, random_play)
        if w == 0:
            continue
        counts[w - 1] += 1
    print('Wins', counts)


if __name__ == '__main__':
    random.seed(1337)
    main()
