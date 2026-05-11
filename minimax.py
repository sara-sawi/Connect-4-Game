import math
from game_logic import drop_piece, check_win
from evaluation import evaluate_board, evaluate_board_v2

ROWS = 6
COLS = 7
AI_PIECE = 2
PLAYER_PIECE = 1

# =========================
# AI STATS (for GUI)
# =========================
nodes_explored = 0
move_scores = {}


# =========================
# RESET STATS
# =========================
def reset_stats():
    global nodes_explored, move_scores
    nodes_explored = 0
    move_scores = {}


# =========================
# VALID MOVES
# =========================
def get_valid_locations(board):
    return [col for col in range(COLS) if board[0][col] == 0]


# =========================
# TERMINAL CHECK
# =========================
def is_terminal_node(board):
    return (
        check_win(board, PLAYER_PIECE) or
        check_win(board, AI_PIECE) or
        len(get_valid_locations(board)) == 0
    )


# =========================
# MINIMAX
# =========================
def minimax(
    board,
    depth,
    maximizing_player,
    heuristic_func,
    original_depth=None
):

    global nodes_explored, move_scores

    # reset once
    if original_depth is None:
        reset_stats()
        original_depth = depth

    nodes_explored += 1

    valid_locations = get_valid_locations(board)
    terminal = is_terminal_node(board)

    # =========================
    # BASE CASE
    # =========================
    if depth == 0 or terminal:

        if terminal:

            if check_win(board, AI_PIECE):
                return None, 1000000

            elif check_win(board, PLAYER_PIECE):
                return None, -1000000

            else:
                return None, 0

        else:
            return None, heuristic_func(board)

    # =========================
    # MAXIMIZING PLAYER
    # =========================
    if maximizing_player:

        value = -math.inf
        best_col = valid_locations[0]

        for col in valid_locations:

            temp_board = [row[:] for row in board]

            drop_piece(temp_board, col, AI_PIECE)

            _, new_score = minimax(
                temp_board,
                depth - 1,
                False,
                heuristic_func,
                original_depth
            )

            # save scores for GUI
            if depth == original_depth:
                move_scores[col] = new_score

            if new_score > value:
                value = new_score
                best_col = col

        return best_col, value

    # =========================
    # MINIMIZING PLAYER
    # =========================
    else:

        value = math.inf
        best_col = valid_locations[0]

        for col in valid_locations:

            temp_board = [row[:] for row in board]

            drop_piece(temp_board, col, PLAYER_PIECE)

            _, new_score = minimax(
                temp_board,
                depth - 1,
                True,
                heuristic_func,
                original_depth
            )

            if new_score < value:
                value = new_score
                best_col = col

        return best_col, value