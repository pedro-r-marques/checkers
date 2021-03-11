#include "checkers.h"

#include <iostream>

using namespace std;

extern int scorer_test();

namespace {
int test_pawn_moves() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 2, 0, 0,
        0, 0, 1, 0, 1, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        1, 0, 1, 0, 0, 0, 0, 0,
        0, 2, 0, 0, 0, 0, 0, 2,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    });
    // clang-format on
    list<CheckersBoard::Move> capture_moves;
    list<CheckersBoard::Move> non_capture_moves;

    tie(capture_moves, non_capture_moves) =
            board.position_moves(make_pair(5, 1));

    if (!non_capture_moves.empty()) {
        cout << "Position(5, 1): expected non capture moves to be empty"
             << endl;
        return -1;
    }
    if (capture_moves.size() != 1) {
        cout << "Position(5, 1): expected capture moves size to be 1, got "
             << capture_moves.size() << endl;
        return -1;
    }
    CheckersBoard::Move expected_move{{5, 1}, {3, 3}, {1, 1}};
    if (capture_moves.front() != expected_move) {
        cout << "Position(5, 1): unexpected move" << endl;
        return -1;
    }

    tie(capture_moves, non_capture_moves) =
            board.position_moves(make_pair(5, 7));
    if (!capture_moves.empty()) {
        cout << "Position(5, 7): expected capture moves size to be 0, got "
             << capture_moves.size() << endl;
        return -1;
    }
    if (non_capture_moves.size() != 1) {
        cout << "Position(5, 7): expected capture moves size to be 1, got "
             << capture_moves.size() << endl;
        return -1;
    }
    CheckersBoard::Move expected_nc_move({{5, 7}, {4, 6}});
    if (non_capture_moves.front() != expected_nc_move) {
        cout << "Position(5, 7): unexpected move" << endl;
        return -1;
    }

    return 0;
}

int test_king_moves() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 1, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 1, 0,
        0, 0, 0, 1, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0, 3, 0,
        0, 4, 0, 0, 0, 0, 0, 2,
        0, 0, 2, 0, 1, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    });
    // clang-format on
    list<CheckersBoard::Move> capture_moves;
    list<CheckersBoard::Move> non_capture_moves;

    tie(capture_moves, non_capture_moves) =
            board.position_moves(make_pair(5, 1));

    if (non_capture_moves.size() != 2) {
        cout << "Position(5, 1): expected non capture moves size to be 1, got "
             << non_capture_moves.size() << endl;
        return -1;
    }
    if (capture_moves.size() != 1) {
        cout << "Position(5, 1): expected capture moves size to be 1, got "
             << capture_moves.size() << endl;
        return -1;
    }
    CheckersBoard::Move expected_move{{5, 1}, {1, 5}, {3, 7}, {5, 5}, {7, 3}};
    if (capture_moves.front() != expected_move) {
        cout << "Position(5, 1): unexpected move" << endl;
        return -1;
    }
    return 0;
}

int test_exec_move() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 2, 0, 0,
        0, 0, 1, 0, 1, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        1, 0, 1, 0, 0, 0, 0, 0,
        0, 2, 0, 0, 0, 0, 0, 2,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    });
    // clang-format on

    int w_count;
    int b_count;

    tie(w_count, b_count) = board.count();
    CheckersBoard::Move move{{5, 1}, {3, 3}, {1, 1}};
    board.move(move);

    int w_prime;
    int b_prime;
    tie(w_prime, b_prime) = board.count();
    if (w_count - w_prime != 2 || b_count != b_prime) {
        cout << "Unexpected piece counts" << endl;
        return -1;
    }

    if (board.get_position(make_pair(1, 1)) !=
        CheckersBoard::Piece::BLACK_PAWN) {
        cout << "Position(1, 1) missing expected value" << endl;
        return -1;
    }

    return 0;
}

int test_init_moves() {
    CheckersBoard board;
    list<CheckersBoard::Move> moves = board.valid_moves(CheckersBoard::WHITE);
    if (moves.size() != 7) {
        cout << "Expected 7 moves, got " << moves.size() << endl;
        return -1;
    }
    return 0;
}

int test_play_move_sequence() {
    // test hash calculation
    CheckersBoard board;
    static CheckersBoard::Move move_list[] = {
            {{5, 4}, {4, 5}}, {{2, 5}, {3, 4}}, {{6, 3}, {5, 4}},
            {{2, 1}, {3, 0}}, {{7, 2}, {6, 3}}, {{1, 6}, {2, 5}},
            {{5, 0}, {4, 1}}, {{1, 2}, {2, 1}}, {{5, 4}, {4, 3}},
            {{0, 7}, {1, 6}}, {{6, 3}, {5, 4}}, {{2, 3}, {3, 2}},
    };

    const size_t move_list_sz = sizeof(move_list) / sizeof(move_list[0]);
    std::vector<uint64_t> hash_values;
    hash_values.reserve(move_list_sz);

    for (int i = 0; i < move_list_sz; i++) {
        board.move(move_list[i]);
        uint64_t h = board.hash();
        if (std::find(hash_values.begin(), hash_values.end(), h) !=
            hash_values.end()) {
            cout << "Duplicate hash value" << endl;
            return -1;
        }
        hash_values.push_back(h);
    }
    return 0;
}

}  // namespace
int main(int argc, char* argv[]) {
    int result = test_pawn_moves();
    if (result != 0) {
        return result;
    }

    result = test_king_moves();
    if (result != 0) {
        return result;
    }

    result = test_exec_move();
    if (result != 0) {
        return result;
    }

    result = test_init_moves();
    if (result != 0) {
        return result;
    }

    result = test_play_move_sequence();
    if (result != 0) {
        return result;
    }

    result = scorer_test();
    if (result != 0) {
        return result;
    }

    cout << "OK" << endl;
    return 0;
}
