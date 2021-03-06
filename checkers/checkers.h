#ifndef __CHECKERS_CHECKERS_H__
#define __CHECKERS_CHECKERS_H__

#include <array>
#include <list>
#include <tuple>
#include <utility>
#include <vector>

class CheckersBoard {
   public:
    const static int BOARD_SIZE = 8;

    typedef std::pair<int, int> Position;
    typedef std::vector<Position> Move;
    typedef std::vector<uint8_t> PositionPiece;

    enum Player {
        WHITE = 1,
        BLACK = 2,
    };
    enum Piece {
        WHITE_PAWN = 1,
        BLACK_PAWN = 2,
        WHITE_KING = 3,
        BLACK_KING = 4,
    };
    CheckersBoard();
    CheckersBoard(const CheckersBoard &);
    CheckersBoard(const std::vector<int> &);

    void initialize(const std::vector<int> &);

    bool operator==(const CheckersBoard &) const;
    uint64_t hash() const;

    // Returns the number of pieces for each player.
    std::pair<int, int> count() const;

    // Returns the per piece type counts.
    std::array<int, 4> piece_count() const;

    // Returns the lists of possible capture and non-capture moves for
    // the specified player.
    std::list<Move> valid_moves(Player player) const;

    // Returns the lists of possible capture and non-capture moves for the
    // piece in the specified position. The moves may not be valid given
    // that there could be a different position with a larger capture sequence.
    std::pair<std::list<Move>, std::list<Move>> position_moves(
            Position pos) const;

    Piece get_position(Position pos) const;

    std::list<PositionPiece> pieces() const;

    // returns a pointer to an  64 byte array with the board values.
    const char *data() const { return board_.data(); }

    void move(const Move &move);

   private:
    Piece maybe_promote_piece(Position position, Piece piece,
                              Player player) const;
    void clear_position(Position pos);
    void set_position(Position pos, Piece piece);

    std::pair<std::list<Move>, std::list<Move>> generate_pawn_moves(
            Position pos, Player player, bool capture_only,
            const std::list<Position> &prefix) const;

    std::pair<std::list<Move>, std::list<Move>> generate_king_moves(
            Position pos, Player player, bool recursion,
            std::pair<bool, bool> exclude_dir,
            const std::list<Position> &exclude_list,
            const std::list<Position> &prefix) const;

    std::array<char, BOARD_SIZE * BOARD_SIZE> board_;
};

#endif  // __CHECKERS_CHECKERS_H__