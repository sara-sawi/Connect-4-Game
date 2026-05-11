import math
from typing import Tuple, Optional

from game_logic import drop_piece, check_win

from minimax import (
    get_valid_locations,
    is_terminal_node,
    AI_PIECE,
    PLAYER_PIECE
)

from evaluation import evaluate_board, evaluate_board_v2


# =========================
# STATS (AI ANALYSIS)
# =========================
nodes_explored = 0
pruned_nodes = 0
move_scores = {}


# =========================
# RESET STATS
# =========================
def reset_nodes():

    global nodes_explored, pruned_nodes, move_scores

    nodes_explored = 0
    pruned_nodes = 0
    move_scores = {}


# =========================
# MOVE ORDERING
# =========================
def order_moves(board, valid_locations, piece, heuristic_func):

    scored_moves = []

    for col in valid_locations:

        temp_board = [row[:] for row in board]

        drop_piece(temp_board, col, piece)

        score = heuristic_func(temp_board)

        scored_moves.append((col, score))

    reverse = True if piece == AI_PIECE else False

    scored_moves.sort(
        key=lambda x: x[1],
        reverse=reverse
    )

    return [col for col, _ in scored_moves]


# =========================
# ALPHA-BETA PRUNING
# =========================
def alpha_beta(
    board,
    depth: int,
    alpha: float,
    beta: float,
    maximizing_player: bool,
    heuristic_func,
    root: bool = True
) -> Tuple[Optional[int], int]:

    global nodes_explored, pruned_nodes, move_scores

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

        return None, heuristic_func(board)

    # =========================
    # MOVE ORDERING
    # =========================
    if maximizing_player:

        valid_locations = order_moves(
            board,
            valid_locations,
            AI_PIECE,
            heuristic_func
        )

    else:

        valid_locations = order_moves(
            board,
            valid_locations,
            PLAYER_PIECE,
            heuristic_func
        )

    # =========================
    # MAX PLAYER
    # =========================
    if maximizing_player:

        value = -math.inf

        best_col = valid_locations[0]

        for col in valid_locations:

            temp_board = [row[:] for row in board]

            drop_piece(temp_board, col, AI_PIECE)

            _, new_score = alpha_beta(
                temp_board,
                depth - 1,
                alpha,
                beta,
                False,
                heuristic_func,
                False
            )

            # save scores for GUI
            if root:
                move_scores[col] = new_score

            if new_score > value:

                value = new_score
                best_col = col

            alpha = max(alpha, value)

            # pruning
            if alpha >= beta:

                pruned_nodes += 1
                break

        return best_col, value

    # =========================
    # MIN PLAYER
    # =========================
    else:

        value = math.inf

        best_col = valid_locations[0]

        for col in valid_locations:

            temp_board = [row[:] for row in board]

            drop_piece(temp_board, col, PLAYER_PIECE)

            _, new_score = alpha_beta(
                temp_board,
                depth - 1,
                alpha,
                beta,
                True,
                heuristic_func,
                False
            )

            if new_score < value:

                value = new_score
                best_col = col

            beta = min(beta, value)

            # pruning
            if alpha >= beta:

                pruned_nodes += 1
                break

        return best_col, value