// global state
var currentBoard = undefined;
var selectedCell = null;
var currentPlayOptions = [];
var gameRunning = false;

var computerPlayer = (optStartingPlayer == 1) ? 2 : 1;

let sValue = sessionStorage.getItem("computerPlayer");
if (sValue != null) {
    computerPlayer = parseInt(sValue);
}
var computerLevel = 2;


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

    for (i = 0; i < 8; i++) {
        for (j = 0; j < 8; j++) {
            let piece = board[i][j];

            let row = (optYOrigin == 1) ? i : 7 - i;
            var col = j;
            if (computerPlayer == optStartingPlayer) {
                row = 7 - row;
                col = 7 - col;
            }
            let tr = tbody.rows[row];
            let td = tr.cells[col + 1];

            switch (piece) {
                case 0:
                    td.innerHTML = "";
                    td.classList.remove('white-piece');
                    td.classList.remove('black-piece');
                    break;
                case 1:
                    td.innerHTML = "&#x26c0;";
                    td.classList.add('white-piece');
                    break;
                case 2:
                    td.innerHTML = "&#x26c2;";
                    td.classList.add('black-piece');
                    break;
                case 3:
                    td.innerHTML = "&#x26c1;";
                    td.classList.add('white-piece');
                    break;
                case 4:
                    td.innerHTML = "&#x26c3;";
                    td.classList.add('black-piece');
                    break;
            }
        }
    }

    // Update the score box
    el_count_computer = document.querySelector("#computer-capture-count");
    el_count_player = document.querySelector("#player-capture-count");
    let white_captures = 12 - response['pieces'][1];
    let black_captures = 12 - response['pieces'][0];
    if (computerPlayer == 1) {
        el_count_computer.innerHTML = white_captures.toString();
        el_count_player.innerHTML = black_captures.toString();
    } else {
        el_count_computer.innerHTML = black_captures.toString();
        el_count_player.innerHTML = white_captures.toString();
    }

    // Update the game-over box.
    gameRunning = response['pieces'].every(value => (value > 0));
    let game_over_div = document.querySelector("div.game-over");
    let game_over_box = game_over_div.querySelector("dl");
    let win = game_over_box.querySelector("#winner");

    if (gameRunning) {
        game_over_box.style.visibility = "hidden";
        win.innerHTML = "";
    } else {
        game_over_box.style.visibility = "visible";
        if (response['pieces'][0] == 0) {
            let playerDesc = (computerPlayer == 1) ? "Player" : "Computer";
            win.innerHTML = playerDesc + " (black) wins";
        } else {
            let playerDesc = (computerPlayer == 1) ? "Computer" : "Player";
            win.innerHTML = playerDesc + " (white) wins";
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

        // coordinates to table cell
        if (optYOrigin == 0) {
            row = 7 - row;
        }
        if (computerPlayer == optStartingPlayer) {
            row = 7 - row;
            col = 7 - col;
        }

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

        // coordinates to table cell
        if (optYOrigin == 0) {
            row = 7 - row;
        }
        if (computerPlayer == optStartingPlayer) {
            row = 7 - row;
            col = 7 - col;
        }

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
    let humanPlayer = (computerPlayer == 1) ? 2 : 1;
    let request_data = {
        'player': humanPlayer,
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
        'player': computerPlayer,
        'auto': true,
        'level': computerLevel,
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

function isComputerPiece(value) {
    switch (computerPlayer) {
        case 1:
            return value == 1 || value == 3;
        case 2:
            return value == 2 || value == 4;
    }
    return false;
}
function onCellClick(element, event) {
    // Handle a click on the checkers board
    // Clicking on a piece selects that piece to move and displays potential
    // move options; clicking on one of the move options triggers the move.
    let row = parseInt(element.getAttribute("row"));
    let col = parseInt(element.getAttribute("col"));

    // table cell to coordinates
    if (optYOrigin == 0) {
        row = 7 - row;
    }
    if (computerPlayer == optStartingPlayer) {
        row = 7 - row;
        col = 7 - col;
    }

    const value = currentBoard[row][col];
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
    } else if (!isComputerPiece(value)) {
        if (selectedCell != null) {
            clearPlayOptions(selectedCell[0], selectedCell[1]);
        }
        selectedCell = [row, col];
        if (gameRunning) {
            getPlayOptions(row, col);
        }
    } else if (isComputerPiece(value)) {
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

    let p = fetch('/api/restart', { 'method': 'POST' })
        .then((response) => {
            if (response.status != 200) {
                console.log(response);
            }
            return board_update();
        });

    if (computerPlayer == optStartingPlayer) {
        p.then(function () { advanceGame(); })
    }
};

function settingsSetup() {
    var playerInputs = ["playerSelectionWhite", "playerSelectionBlack"];
    for (var i = 0; i < playerInputs.length; i++) {
        var element = document.getElementById(playerInputs[i]);
        element.checked = (i == computerPlayer - 1);
    }

    var levelInputs = ["levelSelector1", "levelSelector2", "levelSelector3"];
    for (var i = 0; i < levelInputs.length; i++) {
        var element = document.getElementById(levelInputs[i]);
        element.checked = (i == computerLevel - 1);
    }
}

function updateCoordinates(nplayer) {
    let xboard = document.querySelector("#board");
    let thead = xboard.querySelector("thead");
    for (var i = 0; i < 8; i++) {
        let col = i;
        if (nplayer == 2) {
            col = 7 - col;
        }
        let chr = String.fromCharCode("a".codePointAt(0) + col);
        let element = thead.rows[0].cells[i + 1];
        element.innerHTML = chr;
    }

    let tbody = xboard.querySelector("tbody");
    for (var i = 0; i < 8; i++) {
        let tr = tbody.rows[i];
        let row = (optYOrigin == 1) ? i : 7 - i;
        if (nplayer == optStartingPlayer) {
            row = 7 - row;
        }
        let element = tr.cells[0];
        element.innerHTML = String.fromCharCode("0".codePointAt(0) + row);
    }
}

function settingsChange() {
    var playerInputs = ["playerSelectionWhite", "playerSelectionBlack"];
    var nplayer = computerPlayer;
    for (var i = 0; i < playerInputs.length; i++) {
        var element = document.getElementById(playerInputs[i]);
        if (element.checked) {
            nplayer = i + 1;
        }
    }

    var levelInputs = ["levelSelector1", "levelSelector2", "levelSelector3"];
    for (var i = 0; i < levelInputs.length; i++) {
        var element = document.getElementById(levelInputs[i]);
        if (element.checked) {
            computerLevel = i + 1;
        }
    }

    let settingsModelElement = document.getElementById('settingsModal');
    let modal = bootstrap.Modal.getInstance(settingsModelElement);
    modal.hide();

    if (nplayer != computerPlayer) {
        updateCoordinates(nplayer);
        computerPlayer = nplayer;
        sessionStorage.setItem("computerPlayer", nplayer.toString());
        game_restart();
    }
}

function initialize() {
    // Register event listeners and fetch the board contents.
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

    let settingsElement = document.getElementById('settingsModal');
    settingsElement.addEventListener('show.bs.modal', function (event) {
        settingsSetup();
    });
    let settingsOK = document.getElementById('settings-btn-ok');
    settingsOK.addEventListener('click', function (event) {
        settingsChange();
    });

    let loadModealElement = document.getElementById('loadingModal');
    let loadModal = new bootstrap.Modal(loadModealElement, { keyboard: false });
    loadModal.show();
    let boardLoadPromise = board_update();
    loadModealElement.addEventListener('shown.bs.modal', function (event) {
        boardLoadPromise.then(function () { loadModal.hide(); })
    });


    let btn_restart = document.querySelector("#restart");
    btn_restart.addEventListener("click", function (event) {
        game_restart();
    });

}

document.addEventListener("DOMContentLoaded", () => {
    initialize();
})