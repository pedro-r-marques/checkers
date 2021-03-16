var turn = 0;
var turn_count = 0;

function move_repr(move) {
    if (move == null) {
        return "None";
    }
    let str = "";
    move.forEach(element => {
        if (str.length) {
            str += " ";
        }
        let chr = String.fromCharCode("a".codePointAt(0) + element[1]);
        str += "(" + element[0] + ", " + chr + ")";
    });
    return "[" + str + "]";
}

function show_board(response) {
    let board = new Array(8);
    for (i = 0; i < 8; i++) {
        board[i] = new Array(8).fill(0);
    }

    response['board'].forEach(element => {
        let row = element[0];
        let col = element[1];
        board[row][col] = element[2];
    });

    currentBoard = board;

    // Update the HTML elements. Table elements that have a piece are assigned
    // html text and a color class; elements with no piece have this properties
    // reset.
    let xboard = document.querySelector("#board");
    let tbody = xboard.querySelector("tbody");

    move_info = response['move'];
    move_end = move_info[move_info.length - 1];

    for (row = 0; row < 8; row++) {
        for (col = 0; col < 8; col++) {
            let piece = board[row][col];
            let tr = tbody.rows[row];
            let td = tr.cells[col + 1];

            if (row == move_end[0] && col == move_end[1]) {
                td.classList.add('move-end');
            } else {
                td.classList.remove('move-end');
            }

            if (piece == 0) {
                td.innerHTML = "";
                td.classList.remove('white-piece');
                td.classList.remove('black-piece');
            } else {
                if (piece == 1 || piece == 2) {
                    td.innerHTML = "x";
                } else {
                    td.innerHTML = "X";
                }
                if (piece == 1 || piece == 3) {
                    td.classList.add('white-piece');
                    td.classList.remove('black-piece');
                } else {
                    td.classList.add('black-piece');
                    td.classList.remove('white-piece');
                }
            }
        }
    }

    let el_result = document.querySelector("#result");
    last_turn_counts = response['result'];
    if (last_turn_counts[0] == 0) {
        el_result.innerHTML = "BLACK wins";
    } else if (last_turn_counts[1] == 0) {
        el_result.innerHTML = "WHITE wins";
    } else {
        el_result.innerHTML = "";
    }

    let el_player = document.querySelector("#player-id");
    switch (response['player']) {
        case 1:
            el_player.innerHTML = 'WHITE';
            break;
        case 2:
            el_player.innerHTML = 'BLACK';
            break;
        default:
            el_player.innerHTML = '';
            break;
    }

    let el_move_descr = document.querySelector("#move-positions");
    el_move_descr.innerHTML = move_repr(move_info);
}

function show_trace(trace_path) {
    var repr = "";
    trace_path.forEach(entry => {
        if (repr.length) {
            repr += ", ";
        }
        repr += move_repr(entry[0])
    });
    return repr;
}

function show_probabilities(plist) {
    if (plist == null) {
        return "";
    }
    var repr = "[";
    plist.forEach(pvalue => {
        if (repr.length > 1) {
            repr += ", "
        }
        repr += pvalue.toFixed(4);
    })
    return repr + "]";
}

function show_debug(move_list) {
    let xtable = document.querySelector("#table-moves");
    let prev_tbody = xtable.querySelector("tbody");
    var tbody = document.createElement('tbody');

    move_list.forEach(move_entry => {
        let tr = tbody.insertRow();
        let td = tr.insertCell();
        td.innerHTML = move_repr(move_entry['move']);
        td.style.whiteSpace = "nowrap";
        td = tr.insertCell();
        td.innerHTML = move_entry['score'].toString();
        td = tr.insertCell();
        if ("probabilities" in move_entry) {
            td.innerHTML = show_probabilities(move_entry['probabilities']);
        }
        td = tr.insertCell();
        if ("pmf" in move_entry) {
            td.innerHTML = move_entry['pmf'].toFixed(4);
        }
        td = tr.insertCell();
        td.innerHTML = show_trace(move_entry['trace']);
    });
    xtable.replaceChild(tbody, prev_tbody);
}

function turn_value_update() {
    let el_turn_count = document.querySelector("#turn-count");
    el_turn_count.innerHTML = turn_count.toString();

    t_input = document.querySelector('#input-move-n');
    t_input.setAttribute("value", turn.toString());
    let turn_max = turn_count - 1;
    t_input.setAttribute("max", turn_max.toString());
}

function update() {
    fetch('/api/move/' + turn.toString())
        .then(response => response.json())
        .then(function (data) {
            turn_count = data['n_turns'];
            show_board(data);
            turn_value_update();
            show_debug(data['debug'])
        });
}

function turn_prev() {
    if (turn == 0) {
        return;
    }
    turn = turn - 1;
    update();
}

function turn_next() {
    if (turn + 1 >= turn_count) {
        return;
    }
    turn = turn + 1;
    update();
}

function turn_input(event) {
    let v = parseInt(event.target.value);
    if (v >= 0 && v < turn_count) {
        turn = v;
        update();
    }
}

function initialize() {
    let btn_prev = document.querySelector("#btn-prev");
    btn_prev.addEventListener("click", function (event) {
        turn_prev();
    });

    let btn_next = document.querySelector("#btn-next");
    btn_next.addEventListener("click", function (event) {
        turn_next();
    });

    let t_input = document.querySelector("#input-move-n");
    t_input.addEventListener("input", function (event) {
        turn_input(event);
    });

    update();
}

document.addEventListener("DOMContentLoaded", () => {
    initialize();
})