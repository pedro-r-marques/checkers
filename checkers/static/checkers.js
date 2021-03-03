// global state
var currentBoard = undefined;
var selectedCell = null;
var currentPlayOptions = [];
var gameRunning = false;

function board_update_content(response) {
    // Update the board given the response from the webserver

    // Create the state of all the board positions
    // positions start as empty and are then populated from the server
    // response which contains a list of triples of the form (row, col, piece)
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
                if (piece == 1 || piece == 2) {
                    td.innerHTML = "x";
                } else {
                    td.innerHTML = "X";
                }
                if (piece == 1 || piece == 3) {
                    td.classList.add('white-piece');
                } else {
                    td.classList.add('black-piece');
                }
            }
        }
    }

    // Update the score box
    el_count_computer = document.querySelector("#computer-capture-count");
    let value = 12 - response['pieces'][1];
    el_count_computer.innerHTML = value.toString();
    el_count_player = document.querySelector("#player-capture-count");
    value = 12 - response['pieces'][0];
    el_count_player.innerHTML = value.toString();

    // Update the game-over box.
    gameRunning = response['pieces'].every(value => (value > 0));
    let game_over_div = document.querySelector("div.game-over");
    let win = game_over_div.querySelector("#winner");

    if (gameRunning) {
        game_over_div.style.display = "none";
        win.innerHTML = "";
    } else {
        game_over_div.style.display = "block";
        if (response['pieces'][0] == 0) {
            win.innerHTML = "Player (black) wins";
        } else {
            win.innerHTML = "Computer (white) wins";
        }
    }
}

function board_clear() {
    let xboard = document.querySelector("#board");
    let tbody = xboard.querySelector("tbody");

    for (row = 0; row < 8; row++) {
        for (col = 0; col < 8; col++) {
            let tr = tbody.rows[row];
            let td = tr.cells[col + 1];

            td.innerHTML = "";
            td.classList.remove('white-piece');
            td.classList.remove('black-piece');
        }
    }
}

function board_update() {
    return fetch('/api/board')
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
    // When a user clicks on one of its pieces, fetch the possible moves and
    // highlight them on the board
    let path = '/api/moves/' + row.toString() + '/' + col.toString();
    return fetch(path)
        .then(response => response.json())
        .then(function (data) {
            currentPlayOptions = data;
            showPlayOptions();
        });
}

function clearPlayOptions(row, col) {
    // Remove any position highlights
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

    let element = document.querySelector('#last-move')
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

    return fetch('/api/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request_data)
    }).then(
        function (response) {
            return board_update();
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
            return board_update();
        });

}

function onCellClick(element, event) {
    // Handle a click on the checkers board
    // Clicking on a piece selects that piece to move and displays potential
    // move options; clicking on one of the move options triggers the move.
    const row = parseInt(element.getAttribute("row"));
    const col = parseInt(element.getAttribute("col"));

    let value = currentBoard[row][col];
    if (value == 0) {
        if (selectedCell == null || !gameRunning) {
            return;
        }
        if (isInCurrentOptions(row, col)) {
            let promise = makeMove(selectedCell, [row, col]);
            clearPlayOptions(selectedCell[0], selectedCell[1]);
            selectedCell = null;
            promise.then(function () {
                if (gameRunning) {
                    advanceGame();
                }
            });
        }
    } else if (value == 2 || value == 4) {
        if (selectedCell != null) {
            clearPlayOptions(selectedCell[0], selectedCell[1]);
        }
        selectedCell = [row, col];
        if (gameRunning) {
            getPlayOptions(row, col);
        }
    } else if (value == 1 || value == 3) {
        if (selectedCell != null) {
            clearPlayOptions(selectedCell[0], selectedCell[1]);
        }
        selectedCell = null;
    }
}

function game_restart() {
    // Called when the user clicks on the restart button.
    // Cleans up last-move and play-options and sends a restart
    // request to the web server.
    let element = document.querySelector('#last-move')
    element.innerHTML = "";

    if (selectedCell != null) {
        clearPlayOptions(selectedCell[0], selectedCell[1]);
        selectedCell = null;
    }

    board_clear();

    fetch('/api/restart', { 'method': 'POST' })
        .then((response) => {
            if (response.status != 200) {
                console.log(response);
            }
            board_update();
        });
};

function initialize() {
    // Register event listeners and fetch the board contents.
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
            });
        }
    }

    let btn_restart = document.querySelector("#restart");
    btn_restart.addEventListener("click", function (event) {
        game_restart();
    });

}

document.addEventListener("DOMContentLoaded", () => {
    initialize();
})