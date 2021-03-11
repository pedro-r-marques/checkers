#ifndef __CHECKERS_SCORER_H__
#define __CHECKERS_SCORER_H__

#include "checkers.h"

class Scorer {
   public:
    static const int SCORE_MAX = 1000;
    static const int SCORE_MIN = -SCORE_MAX;

    typedef CheckersBoard::Piece Piece;
    typedef CheckersBoard::Player Player;

    struct Params {
        int piece_value;
        int king_value;
        int piece_1away_value;
        int piece_naway_value;
    };
    Scorer();
    Scorer(const Params&);
    int score(const CheckersBoard& board, Player player);

   private:
    static const Params default_params;
    Params params_;
};

#endif  // __CHECKERS_SCORER_H__
