import random

ROWS = 6
COLS = 7

def create_board():
    """Create a 6x7 board filled with 0s"""
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]


def print_board(board):
    """Print the board to console"""
    for row in board:
        print(row)
    print("\n")


def is_valid_location(board, col):
    """Check if the top of the column is empty"""
    return board[0][col] == 0


def get_next_open_row(board, col):
    """Return the row index of the next open spot in the column"""
    for r in reversed(range(ROWS)):
        if board[r][col] == 0:
            return r
    return None  # Column full


def drop_piece(board, col, piece):
    """
    Place a piece (1 or 2) in the chosen column.
    Returns True if successful, False if the column is full
    """
    row = get_next_open_row(board, col)
    if row is not None:
        board[row][col] = piece
        return True
    else:
        return False


def check_win(board, piece):
    """Check horizontal, vertical, and diagonal wins for the given piece"""

    # Check horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    # Check vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    # Check positively sloped diagonal (/)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True

    # Check negatively sloped diagonal (\)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    return False


# 🔥 NEW FEATURE: Random board generator
def randomize_board(board, moves=12):

    count = 0

    while count < moves:

        col = random.randint(0, COLS - 1)

        if is_valid_location(board, col):

            temp = [row[:] for row in board]

            piece = 1 if count % 2 == 0 else 2

            drop_piece(temp, col, piece)

            if not check_win(temp, piece):
                drop_piece(board, col, piece)
                count += 1
