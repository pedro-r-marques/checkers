""" Defines the checkers board and implements the rules of the game.
"""
import hashlib


class CheckersBoard():
    """ CheckersBoard class and associated methods.
    """

    WHITE = 1
    BLACK = 2
    WHITE_KING = 3
    BLACK_KING = 4

    BOARD_SIZE = 8
    NUM_PIECES = 12  # Number of pieces per player

    def __init__(self, initial_state=None):
        if initial_state is None:
            self.board = CheckersBoard.initial_board()
        else:
            self.board = [x[:] for x in initial_state]
        self._hash_value = None

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        if self._hash_value is not None:
            return self._hash_value

        pieces = self.pieces()
        h = hashlib.md5()
        for piece in pieces:
            h.update(bytes(piece))
        v = int(h.hexdigest()[-15:], 16)

        self._hash_value = v
        return v

    @classmethod
    def initial_board(cls):
        board = [[0] * cls.BOARD_SIZE for _ in range(cls.BOARD_SIZE)]
        for i in range(3):
            offset = 0 if i == 1 else 1
            for j in range(4):
                n = j * 2 + offset
                board[i][n] = cls.WHITE

        for i in range(3):
            offset = 1 if i == 1 else 0
            for j in range(4):
                n = j * 2 + offset
                board[7 - i][n] = cls.BLACK

        return board

    @classmethod
    def copy(cls, obj):
        return CheckersBoard(initial_state=obj.board)

    def count(self):
        """ Returns the number of white and black pieces in the board.
        """
        w_count = 0
        b_count = 0
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                v = self.board[i][j]
                if v in [self.WHITE, self.WHITE_KING]:
                    w_count += 1
                elif v in [self.BLACK, self.BLACK_KING]:
                    b_count += 1

        return w_count, b_count

    def piece_count(self):
        """ Returns the per piece type counts.
        """
        counts = [0] * 4
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                v = self.board[i][j]
                if v == 0:
                    continue
                counts[v - 1] += 1
        return counts

    @classmethod
    def _is_player_piece(cls, v, player):
        if player == cls.WHITE:
            return v in [cls.WHITE, cls.WHITE_KING]
        elif player == cls.BLACK:
            return v in [cls.BLACK, cls.BLACK_KING]
        return False

    @classmethod
    def _is_opposing_player_piece(cls, v, player):
        if player == cls.WHITE:
            return v in [cls.BLACK, cls.BLACK_KING]
        elif player == cls.BLACK:
            return v in [cls.WHITE, cls.WHITE_KING]
        return False

    def _generate_piece_moves(self, row, col, player, capture_only=False):
        """ pieces (men) can move forwards only.
        """
        nrow = row + 1 if player == self.WHITE else row - 1
        if nrow < 0 or nrow >= self.BOARD_SIZE:
            return [], []

        capture_moves = []
        non_capture_moves = []

        def gen_capture_move(nnrow, nncol):
            additional, _ = self._generate_piece_moves(
                nnrow, nncol, player, capture_only=True)
            if additional:
                for m in additional:
                    capture_moves.append([(row, col)] + m)
            else:
                capture_moves.append([(row, col), (nnrow, nncol)])

        # left diagnonal
        if col > 0:
            v = self.board[nrow][col-1]
            if v == 0:
                if not capture_only:
                    non_capture_moves.append([(row, col), (nrow, col - 1)])
            elif col > 1 and self._is_opposing_player_piece(v, player):
                nnrow = nrow + 1 if player == self.WHITE else nrow - 1
                if nnrow >= 0 and nnrow < 8 and self.board[nnrow][col - 2] == 0:
                    gen_capture_move(nnrow, col - 2)

        # right diagnonal
        if col < self.BOARD_SIZE - 1:
            v = self.board[nrow][col+1]
            if v == 0:
                if not capture_only:
                    non_capture_moves.append([(row, col), (nrow, col + 1)])
            elif (col < self.BOARD_SIZE - 2 and
                  self._is_opposing_player_piece(v, player)):
                nnrow = nrow + 1 if player == self.WHITE else nrow - 1
                if (nnrow >= 0 and nnrow < self.BOARD_SIZE and
                        self.board[nnrow][col + 2] == 0):
                    gen_capture_move(nnrow, col + 2)

        return capture_moves, non_capture_moves

    def _generate_king_moves(self, row, col, player, capture_only=False,
                             exclude_dir=None, exclude_list=None, depth=0):
        """ kings can move in any diagonal (forward or backwards) and capture
            an opposing piece if there is an empty space beyond it.
        """
        def _advance(pos, vdir, hdir):
            row = pos[0] + (1 if vdir else -1)
            col = pos[1] + (1 if hdir else -1)
            return row, col

        def _is_valid_position(pos):
            return all(c >= 0 and c < self.BOARD_SIZE for c in pos)

        capture_moves = []
        non_capture_moves = []

        start = (row, col)
        if exclude_list is None:
            exclude_list = []

        for diagonal in range(4):
            vdir = diagonal // 2
            hdir = diagonal % 2

            if (vdir, hdir) == exclude_dir:
                continue
            pos = start
            capture = False
            while True:
                pos = _advance(pos, vdir, hdir)
                if not _is_valid_position(pos):
                    break
                v = self.get_position(pos)
                if self._is_player_piece(v, player):
                    break
                if pos in exclude_list:
                    break
                if self._is_opposing_player_piece(v, player):
                    npos = _advance(pos, vdir, hdir)
                    if not _is_valid_position(npos):
                        break
                    if self.get_position(npos) != 0:
                        break
                    capture = True
                    exclude_list.append(pos)
                    pos = npos

                if capture:
                    assert depth < 32
                    additional, _ = self._generate_king_moves(
                        pos[0], pos[1], player, capture_only=True,
                        exclude_dir=(not vdir, not hdir),
                        exclude_list=exclude_list.copy(),
                        depth=depth + 1)
                    if additional:
                        capture_moves.extend([[start] + m for m in additional])
                        continue

                if capture:
                    capture_moves.append([start, pos])
                elif not capture_only:
                    non_capture_moves.append([start, pos])

        return capture_moves, non_capture_moves

    def valid_moves(self, player, select_capture=False):
        """
          Returns: list of valid moves where a move is described by a tuple
          with begin, end coordinates for a piece.
        """
        if player not in [self.BLACK, self.WHITE]:
            raise ValueError('Invalid value for player: %r', player)

        move_lists = [[], []]
        for i in range(8):
            for j in range(8):
                v = self.board[i][j]
                if not self._is_player_piece(v, player):
                    continue

                if player == v:
                    pos_moves = self._generate_piece_moves(i, j, player)
                else:
                    pos_moves = self._generate_king_moves(i, j, player)

                for gbl_list, pos_list in zip(move_lists, pos_moves):
                    assert all(self.get_position(pos) == 0
                               for move in pos_list for pos in move[1:])
                    gbl_list.extend(pos_list)

        if select_capture:
            if move_lists[0]:
                return move_lists[0]
            return move_lists[1]
        return move_lists[0] + move_lists[1]

    def valid_position_moves(self, position, select_capture=False):
        row, col = position
        v = self.board[row][col]
        if v in [self.WHITE, self.WHITE_KING]:
            player = self.WHITE
        elif v in [self.BLACK, self.BLACK_KING]:
            player = self.BLACK
        else:
            raise ValueError('No piece in specified position')

        if v in [self.WHITE, self.BLACK]:
            capture, non_capture = self._generate_piece_moves(row, col, player)
        if v in [self.WHITE_KING, self.BLACK_KING]:
            capture, non_capture = self._generate_king_moves(row, col, player)

        if select_capture and capture:
            moves = capture
        else:
            moves = capture + non_capture
        assert all(self.get_position(pos) == 0
                   for move in moves for pos in move[1:])
        return moves

    def get_position(self, coordinates):
        return self.board[coordinates[0]][coordinates[1]]

    def _clear_position(self, coordinates):
        self.board[coordinates[0]][coordinates[1]] = 0

    def _set_position(self, coordinates, value):
        self.board[coordinates[0]][coordinates[1]] = value

    def _player_count(self, player):
        """ Check how many pieces this player has. If the count is less than
            12, the player has a piece that has been captured and can be used
            to crown a king.
        """
        count = 0
        for i in range(8):
            for j in range(8):
                v = self.board[i][j]
                if v == player:
                    count += 1
                if ((player == self.WHITE and v == self.WHITE_KING) or
                        (player == self.BLACK and v == self.BLACK_KING)):
                    count += 2
        return count

    def _maybe_promote_piece(self, coordinates, piece, player):
        if piece not in [self.WHITE, self.BLACK]:
            return piece
        if player == self.WHITE and coordinates[0] == 7:
            return self.WHITE_KING
        elif player == self.BLACK and coordinates[0] == 0:
            return self.BLACK_KING
        return piece

    def move(self, move, enable_validation=False):
        """ Changes the board by moving a piece.
            It verifies whether the move is valid and will eat pieces.

            Arguments:
              move: A list of 2 or more positions. Simple moves have only
              a start and end position; however it is possible to eat
              multiple pieces in one move. In this case, the move includes
              the intermediate positions since they may include changes in
              direction.
        """
        start = move[0]
        piece = self.get_position(start)
        if piece in [self.WHITE, self.WHITE_KING]:
            player = self.WHITE
        elif piece in [self.BLACK, self.BLACK_KING]:
            player = self.BLACK
        else:
            raise ValueError(f'Invalid start position {start}')

        if enable_validation:
            allowed_moves = self.valid_position_moves(start)
            if move not in allowed_moves:
                raise ValueError(f'Invalid move {move}')

        self._hash_value = None
        self._clear_position(start)
        pos = start

        def _incr(dir):
            return 1 if dir else - 1

        for i in range(1, len(move)):
            npos = move[i]
            assert self.get_position(npos) == 0
            vdir = npos[0] > pos[0]
            hdir = npos[1] > pos[1]

            while True:
                pos = (pos[0] + _incr(vdir), pos[1] + _incr(hdir))
                if pos == npos:
                    break
                v = self.get_position(pos)
                if v != 0:
                    assert self._is_opposing_player_piece(v, player)
                    self._clear_position(pos)

        piece = self._maybe_promote_piece(move[-1], piece, player)
        self._set_position(move[-1], piece)

    def pieces(self):
        """ Returns the list of all board pieces as (row, col, piece code)
        """
        results = []
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                piece = self.board[i][j]
                if piece == 0:
                    continue
                results.append((i, j, piece))
        return results
