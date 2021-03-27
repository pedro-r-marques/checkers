meta = {
    'title': 'Checkers Online Game',
    'description': "Free Online Checkers Game",
    'lang': 'en',
    'lang_country': 'en-us',
}

nav = {
    'brand': "Checkers",
    'rules': "Rules",
    'settings': "Settings",
}

settings = {
    'computer_player_label': "Computer plays",
    'difficulty_level_label': "Difficulty Level",
    'white': "White",
    'black': "Black",
    'easy': "Easy",
    'medium': "Intermediate",
    'hard': "Hard",
    'close': "Close",
    'ok': "OK",
}

card_text = """
Play checkers online against a computer controlled
player. The black pieces play first. Select a piece
in order to see valid moves from that position.
Click on the destination in order to move the piece
to the highlighted squared.
"""

main = {
    'opt_board': 'board_ytop.html.j2',
    'wait': "Please wait",
    'loading': "Loading...",
    'card_title': "Game Of Checkers",
    'card_text': card_text,
}

pane = {
    'computer_move': "Last computer move",
    'score_caption': "Captured pieces",
    'player': "Player",
    'computer': "Computer",
    'game_over': "Game over",
    'restart': "Restart",
}

js_vars = """
const optStartingPlayer = 2;
const optYOrigin = 1; // down
const optLang = "en";
"""

js = {
    'vars': js_vars,
}

en_vars = dict(meta=meta, nav=nav, settings=settings,
               main=main, pane=pane, js=js)
