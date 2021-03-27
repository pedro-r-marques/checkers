meta = {
    'title': 'Jogos de Damas Online',
    'description': "Jogo de Damas Portuguesas Online Gratuíto",
    'lang': 'pt',
    'lang_country': 'pt-pt',
}

nav = {
    'brand': "Jogo de Damas",
    'rules': "Regras",
    'settings': "Opções",
}

settings = {
    'computer_player_label': "Computador joga",
    'difficulty_level_label': "Level de difficuldatde",
    'white': "Brancas",
    'black': "Pretas",
    'easy': "Fácil",
    'medium': "Intermedio",
    'hard': "Difícil",
    'close': "Fechar",
    'ok': "Aceitar",
}

card_text = """
Jogo de Damas Clássicas segundo as regras Portuguesas.
As peças brancas movimentão-se primeiro. Nas opçcões é
possível selecçionar se o Computador jogas com as peças brancas
ou prretas. Escolha uma peça para ver os lançes válidos a partir
dessa posição. Selecione a posição de destino para mover a peça.
"""

main = {
    'opt_board': "board_ybottom.html.j2",
    'wait': "Aguade por favor",
    'loading': "Inicialização...",
    'card_title': "Jogo de Damas Portuguesas",
    'card_text': card_text,
}

pane = {
    'computer_move': "Ultimo movimento do Computador",
    'score_caption': "Peças capturadas",
    'player': "Jogador",
    'computer': "Computador",
    'game_over': "Victória",
    'restart': "Recomeçar",
}

js_vars = """
const optStartingPlayer = 1;
const optYOrigin = 0; // down
const optLang = "pt";
"""

js = {
    'vars': js_vars,
}

pt_vars = dict(meta=meta, nav=nav, settings=settings,
               main=main, pane=pane, js=js)
