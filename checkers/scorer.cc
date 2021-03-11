#include "scorer.h"

#include <set>

using namespace std;

namespace {
CheckersBoard::Player piece_to_player(CheckersBoard::Piece piece) {
    switch (piece) {
        case CheckersBoard::Piece::WHITE_PAWN:
        case CheckersBoard::Piece::WHITE_KING:
            return CheckersBoard::Player::WHITE;
        case CheckersBoard::Piece::BLACK_PAWN:
        case CheckersBoard::Piece::BLACK_KING:
            return CheckersBoard::Player::BLACK;
    }
    throw std::invalid_argument("Invalid piece value");
}

bool is_opposing_player_king(CheckersBoard::Piece piece,
                             CheckersBoard::Player player) {
    switch (player) {
        case CheckersBoard::WHITE:
            if (piece == CheckersBoard::BLACK_KING) {
                return true;
            }
            break;
        case CheckersBoard::BLACK:
            if (piece == CheckersBoard::WHITE_KING) {
                return true;
            }
            break;
    }
    return false;
}

std::vector<CheckersBoard::Position> piece_has_path_forward(
        const CheckersBoard& board, CheckersBoard::Player player,
        CheckersBoard::Position pos, bool vdir) {
    std::vector<CheckersBoard::Position> positions;
    positions.reserve(2);
    for (int i = 0; i < 2; i++) {
        bool hdir = bool(i);
        CheckersBoard::Position npos;
        bool ok;
        tie(npos, ok) = position_advance(pos, vdir, hdir);
        if (!ok) {
            continue;
        }
        auto npiece = board.get_position(npos);
        if (npiece == 0) {
            positions.push_back(npos);
        }
        if (is_opposing_player_piece(npiece, player)) {
            return {};
        }
    }
    return positions;
}
bool piece_has_path_to_promotion(const CheckersBoard& board,
                                 CheckersBoard::Position start, bool vdir,
                                 int distance) {
    CheckersBoard::Player player = piece_to_player(board.get_position(start));

    std::set<CheckersBoard::Position> positions{start};
    for (int i = 0; i < distance; i++) {
        std::set<CheckersBoard::Position> npos_set;
        for (auto pos : positions) {
            auto fwd_path = piece_has_path_forward(board, player, pos, vdir);
            std::copy(fwd_path.begin(), fwd_path.end(),
                      std::inserter(npos_set, npos_set.begin()));
        }
        if (npos_set.empty()) {
            return false;
        }
        positions.swap(npos_set);
    }
    return true;
}

bool piece_is_1step_from_promotion(const CheckersBoard& board,
                                   CheckersBoard::Position pos, bool vdir) {
    // Returns true there is a free path to promotion.
    CheckersBoard::Player player = piece_to_player(board.get_position(pos));

    auto positions = piece_has_path_forward(board, player, pos, vdir);
    if (positions.empty()) {
        return false;
    }

    // look for an opposing king in the diagonals opposite from vdir
    for (int i = 0; i < 2; i++) {
        bool hdir = bool(i);

        CheckersBoard::Position npos;
        bool ok;
        tie(npos, ok) = position_advance(pos, !vdir, hdir);
        while (ok) {
            auto npiece = board.get_position(npos);
            if (npiece != 0) {
                if (is_opposing_player_king(npiece, player)) {
                    return false;
                }
                break;
            }
            tie(npos, ok) = position_advance(npos, !vdir, hdir);
        }
    }

    return true;
}
}  // namespace
const Scorer::Params Scorer::default_params = {
        .piece_value = 10,
        .king_value = 100,
        .piece_1away_value = 50,
        .piece_2away_value = 25,
};

Scorer::Scorer() : params_(default_params) {}
Scorer::Scorer(const Params& params) : params_(params) {}

int Scorer::score(const CheckersBoard& board, Player player) {
    const auto& data = board.board();
    std::array<int, 4> piece_counts;
    piece_counts.fill(0);
    int w_path_count = 0;
    int b_path_count = 0;
    int score = 0;

    for (int i = 0; i < data.size(); i++) {
        Piece piece = static_cast<Piece>(data[i]);
        if (piece == 0) {
            continue;
        }
        piece_counts[piece - 1] += 1;
        const int row = i >> 3;
        const int col = i & 7;

        int distance = 0;
        bool vdir = false;
        switch (piece) {
            case Piece::BLACK_PAWN:
                vdir = false;
                distance = row;
                break;
            case Piece::WHITE_PAWN:
                vdir = true;
                distance = CheckersBoard::BOARD_SIZE - 1 - row;
                break;
            default:
                continue;
        }
        switch (distance) {
            case 1:
                if (piece_is_1step_from_promotion(board, {row, col}, vdir)) {
                    const int factor = is_player_piece(piece, player) ? 1 : -1;
                    score = factor * params_.piece_1away_value;
                }
                break;
            case 2:
                if (piece_has_path_to_promotion(board, {row, col}, vdir,
                                                distance)) {
                    switch (piece) {
                        case Piece::BLACK_PAWN:
                            b_path_count++;
                            break;
                        case Piece::WHITE_PAWN:
                            w_path_count++;
                            break;
                        default:
                            break;
                    }
                }
        }
    }

    int factor = player == CheckersBoard::WHITE ? 1 : -1;

    if ((piece_counts[CheckersBoard::WHITE_PAWN - 1] +
         piece_counts[CheckersBoard::WHITE_KING - 1]) == 0) {
        return -factor * SCORE_MAX;
    }
    if ((piece_counts[CheckersBoard::BLACK_PAWN - 1] +
         piece_counts[CheckersBoard::BLACK_KING - 1]) == 0) {
        return factor * SCORE_MAX;
    }

    int king_delta = piece_counts[CheckersBoard::WHITE_KING - 1] -
                     piece_counts[CheckersBoard::BLACK_KING - 1];
    int piece_delta = piece_counts[CheckersBoard::WHITE_PAWN - 1] -
                      piece_counts[CheckersBoard::BLACK_PAWN - 1];
    score += factor * king_delta * params_.king_value;
    score += factor * piece_delta * params_.piece_value;
    score += factor * w_path_count * params_.piece_2away_value;
    score -= factor * b_path_count * params_.piece_2away_value;

    return score;
}