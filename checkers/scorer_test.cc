#include "scorer.h"

#include <iostream>

using namespace std;

namespace {
int test_init_state() {
    CheckersBoard board;
    Scorer scorer;
    int w_s = scorer.score(board, CheckersBoard::WHITE);
    int b_s = scorer.score(board, CheckersBoard::BLACK);
    if (w_s != 0 || b_s != 0) {
        cout << "Expected 0 scores, got " << w_s << ", " << b_s << endl;
        return 1;
    }
    return 0;
}

int test_win() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 2, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 4, 0, 0, 0, 0, 0, 2,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    });
    // clang-format on

    Scorer scorer;

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != Scorer::SCORE_MIN) {
        cout << "Expected Scorer::SCORE_MIN , got " << score << endl;
        return -1;
    }
    score = scorer.score(board, CheckersBoard::BLACK);
    if (score != Scorer::SCORE_MAX) {
        cout << "Expected Scorer::SCORE_MAX , got " << score << endl;
        return -1;
    }
    return 0;
}

int test_promotion_1step_ok() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 2,
        0, 0, 0, 0, 0, 0, 1, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    });
    // clang-format on
    Scorer scorer(Scorer::Params{.piece_1away_value = 50});

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != 50) {
        cout << "Expected 50, got " << score << endl;
        return -1;
    }
    return 0;
}

int test_promotion_1step_ok_border() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 2,
        1, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    });
    // clang-format on
    Scorer scorer(Scorer::Params{.piece_1away_value = 50});

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != 50) {
        cout << "Expected 50, got " << score << endl;
        return -1;
    }
    return 0;
}

int test_promotion_1step_ok_black() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 1,
        2, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 2,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    });
    // clang-format on
    Scorer scorer(Scorer::Params{.piece_1away_value = 50});

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != -50) {
        cout << "Expected -50, got " << score << endl;
        return -1;
    }
    return 0;
}

int test_promotion_1step_blocked() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 2,
        0, 0, 0, 0, 0, 0, 1, 0,
        0, 0, 0, 0, 0, 0, 0, 2
    });
    // clang-format on
    Scorer scorer(Scorer::Params{.piece_1away_value = 50});

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != 0) {
        cout << "Expected 0, got " << score << endl;
        return -1;
    }
    return 0;
}

int test_promotion_1step_king() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 4, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 2,
        0, 0, 0, 0, 0, 0, 1, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    });
    // clang-format on
    Scorer scorer(Scorer::Params{.piece_1away_value = 50});

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != 0) {
        cout << "Expected 0, got " << score << endl;
        return -1;
    }
    return 0;
}

int test_promotion_1step_protected() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 1, 0, 0, 2,
        0, 0, 0, 1, 0, 0, 0, 0,
        2, 0, 2, 0, 0, 0, 0, 0
    });
    // clang-format on
    Scorer scorer(Scorer::Params{.piece_1away_value = 50});

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != 50) {
        cout << "Expected 50, got " << score << endl;
        return -1;
    }
    return 0;
}

int test_promotion_2step_ok() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 1, 0, 2,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    });
    // clang-format on
    Scorer scorer(Scorer::Params{.piece_2away_value = 25});

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != 25) {
        cout << "test_promotion_2step_ok" << endl;
        cout << "Expected 25, got " << score << endl;
        return -1;
    }
    return 0;
}

int test_promotion_2step_ok_border() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 2, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 2,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    });
    // clang-format on
    Scorer scorer(Scorer::Params{.piece_2away_value = 25});

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != -25) {
        cout << "test_promotion_2step_ok_border" << endl;
        cout << "Expected -25, got " << score << endl;
        return -1;
    }
    return 0;
}

int test_promotion_2step_blocked1() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 1, 0, 2,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 2
    });
    // clang-format on
    Scorer scorer(Scorer::Params{.piece_2away_value = 25});

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != 25) {
        cout << "test_promotion_2step_blocked1" << endl;
        cout << "Expected 25, got " << score << endl;
        return -1;
    }
    return 0;
}

int test_promotion_2step_blocked2() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 1, 0, 2,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 2, 0, 0, 0, 2
    });
    // clang-format on
    Scorer scorer(Scorer::Params{.piece_2away_value = 25});

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != 0) {
        cout << "test_promotion_2step_blocked2" << endl;
        cout << "Expected 0, got " << score << endl;
        return -1;
    }
    return 0;
}

int test_promotion_2step_blocked3() {
    // clang-format off
    CheckersBoard board({
        0, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 1, 0, 2,
        0, 0, 0, 0, 2, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    });
    // clang-format on
    Scorer scorer(Scorer::Params{.piece_1away_value = 25});

    int score = scorer.score(board, CheckersBoard::WHITE);
    if (score != 0) {
        cout << "test_promotion_2step_blocked3" << endl;
        cout << "Expected 0, got " << score << endl;
        return -1;
    }
    return 0;
}

}  // namespace
int scorer_test() {
    typedef int test_function();
    test_function* test_cases[] = {
            test_init_state,
            test_win,
            test_promotion_1step_ok,
            test_promotion_1step_ok_border,
            test_promotion_1step_ok_black,
            test_promotion_1step_blocked,
            test_promotion_1step_protected,
            test_promotion_2step_ok,
            test_promotion_2step_ok_border,
            test_promotion_2step_blocked1,
            test_promotion_2step_blocked2,
            test_promotion_2step_blocked3,
    };
    for (int i = 0; i < (sizeof(test_cases) / sizeof(test_function*)); i++) {
        test_function* fn = test_cases[i];
        int result = (*fn)();
        if (result != 0) {
            return result;
        }
    }
    return 0;
}