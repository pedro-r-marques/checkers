// global state
var currentBoard = undefined;
var selectedCell = null;
var currentPlayOptions = [];

function board_update_content(response) {
    let xboard = document.querySelector("#board");
    let tbody = xboard.querySelector("tbody");

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

    for (row = 0; row < 8; row++) {
        for (col = 0; col < 8; col++) {
            let piece = board[row][col];
            let tr = tbody.rows[row];
            let td = tr.cells[col + 1];

            if (piece == 0) {
                td.innerHTML = "";
                td.classList.remove('white-piece');
                td.classList.remove('black-piece');
            } else {
                td.innerHTML = "x";
                if (piece == 1 || piece == 3) {
                    td.classList.add('white-piece');
                } else {
                    td.classList.add('black-piece');
                }
            }
        }
    }

    el_count_computer = document.querySelector("#computer-capture-count");
    let value = 12 - response['pieces'][1];
    el_count_computer.innerHTML = value.toString();
    el_count_player = document.querySelector("#player-capture-count");
    value = 12 - response['pieces'][0];
    el_count_player.innerHTML = value.toString();
}

function board_update() {
    const response = fetch('/api/board')
        .then(response => response.json())
        .then(function (data) {
            board_update_content(data);
        });
}

function showPlayOptions() {
    let xboard = document.querySelector("#board");
    let tbody = xboard.querySelector("tbody");

    currentPlayOptions.forEach(opt => {
        let end = opt[opt.length - 1];

        let row = end[0];
        let col = end[1];

        let tr = tbody.rows[row];
        let element = tr.cells[col + 1];

        element.innerHTML = '.';
        element.classList.add('play-option');
    });
}

function getPlayOptions(row, col) {
    let path = '/api/moves/' + row.toString() + '/' + col.toString();
    const response = fetch(path)
        .then(response => response.json())
        .then(function (data) {
            currentPlayOptions = data;
            showPlayOptions();
        });
}

function clearPlayOptions(row, col) {
    let xboard = document.querySelector("#board");
    let tbody = xboard.querySelector("tbody");

    currentPlayOptions.forEach(opt => {
        let end = opt[opt.length - 1];

        let row = end[0];
        let col = end[1];

        let tr = tbody.rows[row];
        let element = tr.cells[col + 1];

        element.innerHTML = '';
        element.classList.remove('play-option');
    });

    currentPlayOptions = [];
}

function update_computer_move(response) {
    let str = "";
    response.forEach(element => {
        if (str.length) {
            str += " ";
        }
        let chr = String.fromCharCode("a".codePointAt(0) + element[1]);
        str += "(" + element[0] + ", " + chr + ")";
    });

    element = document.querySelector('#last-move')
    element.innerHTML = str;
}

function isInCurrentOptions(row, col) {
    let exists = currentPlayOptions.some(opt => {
        let end = opt[opt.length - 1];
        return (end[0] == row && end[1] == col);
    });

    return exists;
}

function makeMove(start, end) {
    let request_data = {
        'player': 2,
        'start': start,
        'end': end,
    };

    fetch('/api/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request_data)
    }).then(
        function (response) {
            board_update();
        }
    );
}

function advanceGame() {
    let request_data = {
        'player': 1,
        'auto': true,
    };

    fetch('/api/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request_data)
    })
        .then(response => response.json())
        .then(function (data) {
            update_computer_move(data);
            board_update();
        });

}

function onCellClick(element, event) {
    const row = parseInt(element.getAttribute("row"));
    const col = parseInt(element.getAttribute("col"));

    let value = currentBoard[row][col];
    if (value == 0) {
        if (selectedCell == null) {
            return;
        }
        if (isInCurrentOptions(row, col)) {
            makeMove(selectedCell, [row, col]);
            clearPlayOptions(selectedCell[0], selectedCell[1]);
            selectedCell = null;
            advanceGame();
        }
    } else if (value == 2 || value == 4) {
        if (selectedCell != null) {
            clearPlayOptions(selectedCell[0], selectedCell[1]);
        }
        selectedCell = [row, col];
        getPlayOptions(row, col);
    } else if (value == 1 || value == 3) {
        if (selectedCell != null) {
            clearPlayOptions(selectedCell[0], selectedCell[1]);
        }
        selectedCell = null;
    }
}

function initialize() {

    board_update();

    let xboard = document.querySelector("#board");
    let tbody = xboard.querySelector("tbody");

    for (row = 0; row < 8; row++) {
        for (col = 0; col < 8; col++) {
            let tr = tbody.rows[row];
            let td = tr.cells[col + 1];
            td.setAttribute("row", row.toString());
            td.setAttribute("col", col.toString());
            td.addEventListener("click", function (event) {
                onCellClick(this, event);
            })
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initialize();
})