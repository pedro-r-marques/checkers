#include "checkers.h"

#include <functional>
#include <iostream>
#include <sstream>

using namespace std;

pair<CheckersBoard::Position, bool> position_advance(
        CheckersBoard::Position pos, bool vdir, bool hdir) {
    int row = pos.first + (vdir ? 1 : -1);
    int col = pos.second + (hdir ? 1 : -1);
    if (row >= 0 && row < CheckersBoard::BOARD_SIZE && col >= 0 &&
        col < CheckersBoard::BOARD_SIZE) {
        return make_pair(make_pair(row, col), true);
    }
    return make_pair(make_pair(-1, -1), false);
}

bool is_player_piece(CheckersBoard::Piece piece, CheckersBoard::Player player) {
    switch (piece) {
        case CheckersBoard::Piece::WHITE_PAWN:
        case CheckersBoard::Piece::WHITE_KING:
            return player == CheckersBoard::Player::WHITE;
        case CheckersBoard::Piece::BLACK_PAWN:
        case CheckersBoard::Piece::BLACK_KING:
            return player == CheckersBoard::Player::BLACK;
    }
    return false;
}

bool is_opposing_player_piece(CheckersBoard::Piece piece,
                              CheckersBoard::Player player) {
    return piece != 0 && !is_player_piece(piece, player);
}

namespace {

ostream &operator<<(ostream &os, const CheckersBoard::Position &pos) {
    os << "[" << pos.first << ", " << pos.second << "]";
    return os;
}

ostream &operator<<(ostream &os, const CheckersBoard::Move &move) {
    os << "[";
    for (int i = 0; i < move.size(); i++) {
        if (i > 0) {
            os << ", ";
        }
        os << move[i];
    }
    os << "]";
    return os;
}

template <typename C>
std::string repr(const C &v) {
    stringstream ss;
    ss << v;
    return ss.str();
}

}  // namespace

CheckersBoard::CheckersBoard() {
    board_.fill(0);
    for (int i = 0; i < 3; i++) {
        int offset = (i == 1) ? 0 : 1;
        for (int j = 0; j < 4; j++) {
            int col = j * 2 + offset;
            board_[i * BOARD_SIZE + col] = Piece::WHITE_PAWN;
        }
    }

    for (int i = 0; i < 3; i++) {
        int offset = (i == 1) ? 1 : 0;
        int row = BOARD_SIZE - i - 1;
        for (int j = 0; j < 4; j++) {
            int col = j * 2 + offset;
            board_[row * BOARD_SIZE + col] = Piece::BLACK_PAWN;
        }
    }
}
CheckersBoard::CheckersBoard(const CheckersBoard &rhs) {
    memcpy(board_.data(), rhs.board_.data(), board_.size());
}

CheckersBoard::CheckersBoard(const std::vector<int> &state) {
    if (state.size() != BOARD_SIZE * BOARD_SIZE) {
        throw std::invalid_argument("argument size");
    }
    for (int i = 0; i < board_.size(); i++) {
        board_[i] = state[i];
    }
}

void CheckersBoard::initialize(const std::vector<int> &state) {
    if (state.size() != BOARD_SIZE * BOARD_SIZE) {
        throw std::invalid_argument("argument size");
    }
    for (int i = 0; i < board_.size(); i++) {
        board_[i] = state[i];
    }
}

CheckersBoard::Piece CheckersBoard::maybe_promote_piece(Position position,
                                                        Piece piece,
                                                        Player player) const {
    if (player == Player::WHITE && position.first == BOARD_SIZE - 1) {
        return Piece::WHITE_KING;
    }
    if (player == Player::BLACK && position.first == 0) {
        return Piece::BLACK_KING;
    }
    return piece;
}

CheckersBoard::Piece CheckersBoard::get_position(Position pos) const {
    return static_cast<CheckersBoard::Piece>(
            board_[pos.first * BOARD_SIZE + pos.second]);
}

void CheckersBoard::clear_position(Position pos) {
    board_[pos.first * BOARD_SIZE + pos.second] = 0;
}

void CheckersBoard::set_position(Position pos, Piece piece) {
    board_[pos.first * BOARD_SIZE + pos.second] = piece;
}

std::pair<std::list<CheckersBoard::Move>, std::list<CheckersBoard::Move>>
CheckersBoard::generate_pawn_moves(Position start, Player player,
                                   bool capture_only,
                                   const std::list<Position> &prefix) const {
    bool vdir = player == Player::WHITE ? true : false;

    std::list<Move> capture_moves;
    std::list<Move> non_capture_moves;

    for (int i = 0; i < 2; i++) {
        bool hdir = i > 0;

        Position pos;
        bool ok;
        tie(pos, ok) = position_advance(start, vdir, hdir);
        if (!ok) {
            continue;
        }
        Piece piece = get_position(pos);
        if (piece == 0) {
            if (!capture_only) {
                Move move;
                move.reserve(prefix.size() + 2);
                copy(prefix.begin(), prefix.end(), std::back_inserter(move));
                move.push_back(start);
                move.push_back(pos);
                non_capture_moves.push_back(std::move(move));
            }
            continue;
        }
        if (!is_opposing_player_piece(piece, player)) {
            continue;
        }
        Position npos;
        tie(npos, ok) = position_advance(pos, vdir, hdir);
        if (!ok || get_position(npos) != 0) {
            continue;
        }

        std::list<Move> sub_capture;
        std::list<Move> sub_non_capture;

        list<Position> nprefix(prefix);
        nprefix.push_back(start);

        tie(sub_capture, sub_non_capture) =
                generate_pawn_moves(npos, player, true, nprefix);
        if (!sub_capture.empty()) {
            capture_moves.splice(capture_moves.end(), std::move(sub_capture));
            continue;
        }

        Move move;
        move.reserve(prefix.size() + 2);
        copy(prefix.begin(), prefix.end(), std::back_inserter(move));
        move.push_back(start);
        move.push_back(npos);
        capture_moves.push_back(std::move(move));
    }

    return make_pair(capture_moves, non_capture_moves);
}

std::pair<std::list<CheckersBoard::Move>, std::list<CheckersBoard::Move>>
CheckersBoard::generate_king_moves(Position start, Player player,
                                   bool recursion,
                                   std::pair<bool, bool> exclude_dir,
                                   const std::list<Position> &exclude_list,
                                   const std::list<Position> &prefix) const {
    std::list<Move> capture_moves;
    std::list<Move> non_capture_moves;

    for (int diagonal = 0; diagonal < 4; diagonal++) {
        bool vdir = diagonal >> 1;
        bool hdir = diagonal & 1;

        if (recursion && make_pair(vdir, hdir) == exclude_dir) {
            continue;
        }

        Position pos = start;
        bool capture = false;

        std::list<Move> non_recursive_captures;

        list<Position> n_exclude_list(exclude_list);
        while (true) {
            bool ok;
            tie(pos, ok) = position_advance(pos, vdir, hdir);
            if (!ok) {
                break;
            }
            Piece piece = get_position(pos);
            if (is_player_piece(piece, player)) {
                break;
            }
            if (std::find(exclude_list.begin(), exclude_list.end(), pos) !=
                exclude_list.end()) {
                break;
            }

            if (is_opposing_player_piece(piece, player)) {
                if (capture) {
                    break;
                }
                Position npos;
                bool ok;
                tie(npos, ok) = position_advance(pos, vdir, hdir);
                if (!ok || get_position(npos) != 0) {
                    break;
                }
                capture = true;
                n_exclude_list.push_back(pos);
                pos = npos;
            }

            if (capture) {
                std::list<Move> sub_capture;
                std::list<Move> sub_non_capture;
                list<Position> nprefix(prefix);
                nprefix.push_back(start);
                tie(sub_capture, sub_non_capture) = generate_king_moves(
                        pos, player, true, make_pair(!vdir, !hdir),
                        n_exclude_list, nprefix);
                if (!sub_capture.empty()) {
                    capture_moves.splice(capture_moves.end(),
                                         std::move(sub_capture));
                    non_recursive_captures.clear();
                    break;
                }
            }

            Move move;
            move.reserve(prefix.size() + 2);
            copy(prefix.begin(), prefix.end(), std::back_inserter(move));
            move.push_back(start);
            move.push_back(pos);

            if (capture) {
                non_recursive_captures.push_back(std::move(move));
            } else if (!recursion) {
                non_capture_moves.push_back(std::move(move));
            }
        }
        capture_moves.splice(capture_moves.end(),
                             std::move(non_recursive_captures));
    }

    return make_pair(capture_moves, non_capture_moves);
}

bool CheckersBoard::operator==(const CheckersBoard &rhs) const {
    return memcmp(board_.data(), rhs.board_.data(), board_.size()) == 0;
}

uint64_t CheckersBoard::hash() const {
    return std::hash<string>{}(string(board_.data(), board_.size()));
}

// Returns the number of pieces for each player.
std::pair<int, int> CheckersBoard::count() const {
    int w_count = 0;
    int b_count = 0;

    for (int i = 0; i < BOARD_SIZE * BOARD_SIZE; i++) {
        switch (board_[i]) {
            case CheckersBoard::Piece::WHITE_PAWN:
            case CheckersBoard::Piece::WHITE_KING:
                w_count++;
                break;
            case CheckersBoard::Piece::BLACK_PAWN:
            case CheckersBoard::Piece::BLACK_KING:
                b_count++;
                break;
        }
    }
    return make_pair(w_count, b_count);
}

// Returns the per piece type counts.
std::array<int, 4> CheckersBoard::piece_count() const {
    std::array<int, 4> counts;
    counts.fill(0);

    for (int i = 0; i < BOARD_SIZE * BOARD_SIZE; i++) {
        int piece = board_[i];
        if (piece != 0) {
            counts[piece - 1] += 1;
        }
    }
    return counts;
}

// Returns the lists of possible capture and non-capture moves for
// the specified player.
std::list<CheckersBoard::Move> CheckersBoard::valid_moves(Player player) const {
    std::list<Move> capture_moves;
    std::list<Move> non_capture_moves;

    for (int i = 0; i < BOARD_SIZE * BOARD_SIZE; i++) {
        Piece piece = static_cast<Piece>(board_[i]);
        if (!is_player_piece(piece, player)) {
            continue;
        }
        Position pos = {i >> 3, i & 7};

        list<Move> pos_capture;
        list<Move> pos_non_capture;
        if (piece == Piece::WHITE_KING || piece == Piece::BLACK_KING) {
            tie(pos_capture, pos_non_capture) =
                    generate_king_moves(pos, player, false, {}, {}, {});
        } else {
            tie(pos_capture, pos_non_capture) =
                    generate_pawn_moves(pos, player, false, {});
        }
        capture_moves.splice(capture_moves.end(), std::move(pos_capture));
        non_capture_moves.splice(non_capture_moves.end(),
                                 std::move(pos_non_capture));
    }

    // Implement the rule that player must capture pieces picking the highest
    // capture length.
    if (!capture_moves.empty()) {
        size_t maxlen = 0;
        for (auto &m : capture_moves) {
            maxlen = std::max(maxlen, m.size());
        }
        std::list<Move> max_sz_captures;
        std::copy_if(capture_moves.begin(), capture_moves.end(),
                     std::back_inserter(max_sz_captures),
                     [maxlen](const Move &m) { return m.size() == maxlen; });
        return max_sz_captures;
    }

    return non_capture_moves;
}

// Returns the lists of possible capture and non-capture moves for the
// piece in the specified position.
std::pair<std::list<CheckersBoard::Move>, std::list<CheckersBoard::Move>>
CheckersBoard::position_moves(Position pos) const {
    std::list<CheckersBoard::Move> capture_moves;
    std::list<CheckersBoard::Move> non_capture_moves;

    Piece piece = get_position(pos);
    switch (piece) {
        case WHITE_PAWN:
            tie(capture_moves, non_capture_moves) =
                    generate_pawn_moves(pos, Player::WHITE, false, {});
            break;
        case BLACK_PAWN:
            tie(capture_moves, non_capture_moves) =
                    generate_pawn_moves(pos, Player::BLACK, false, {});
            break;
        case WHITE_KING:
            tie(capture_moves, non_capture_moves) =
                    generate_king_moves(pos, Player::WHITE, false, {}, {}, {});
            break;
        case BLACK_KING:
            tie(capture_moves, non_capture_moves) =
                    generate_king_moves(pos, Player::BLACK, false, {}, {}, {});
            break;
    }
    return make_pair(capture_moves, non_capture_moves);
}

std::list<CheckersBoard::PositionPiece> CheckersBoard::pieces() const {
    std::list<CheckersBoard::PositionPiece> pieces;
    for (int i = 0; i < board_.size(); i++) {
        Piece piece = static_cast<Piece>(board_[i]);
        if (piece == 0) {
            continue;
        }
        int row = i >> 3;
        int col = i & 7;
        pieces.push_back(PositionPiece({static_cast<uint8_t>(row),
                                        static_cast<uint8_t>(col),
                                        static_cast<uint8_t>(piece)}));
    }
    return pieces;
}

void CheckersBoard::move(const CheckersBoard::Move &move) {
    Position start = move[0];
    Piece piece = get_position(start);
    Player player;

    switch (piece) {
        case CheckersBoard::Piece::WHITE_PAWN:
        case CheckersBoard::Piece::WHITE_KING:
            player = CheckersBoard::Player::WHITE;
            break;
        case CheckersBoard::Piece::BLACK_PAWN:
        case CheckersBoard::Piece::BLACK_KING:
            player = CheckersBoard::Player::BLACK;
            break;
        default:
            throw std::invalid_argument("Invalid start position " +
                                        repr(start));
    }

    clear_position(start);
    Position pos = start;

    for (int i = 1; i < move.size(); i++) {
        Position npos = move[i];
        if (get_position(npos) != 0) {
            throw std::invalid_argument("Invalid move position " + repr(npos));
        }
        bool vdir = npos.first > pos.first;
        bool hdir = npos.second > pos.second;

        while (true) {
            bool ok;
            tie(pos, ok) = position_advance(pos, vdir, hdir);
            if (!ok) {
                throw std::out_of_range("Invalid position " + repr(pos));
            }
            if (pos == npos) {
                break;
            }
            Piece intermediate = get_position(pos);
            if (intermediate != 0) {
                if (!is_opposing_player_piece(intermediate, player)) {
                    throw std::invalid_argument("Invalid capture " + repr(pos));
                }
                clear_position(pos);
            }
        }
    }

    Position end = move[move.size() - 1];
    piece = maybe_promote_piece(end, piece, player);
    set_position(end, piece);
}
