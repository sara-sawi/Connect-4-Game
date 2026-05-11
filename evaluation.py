from game_logic import check_win, ROWS, COLS
AI_PIECE = 2
PLAYER_PIECE = 1

# =========================
# SHARED WINDOW EVALUATION
# =========================
def evaluate_window(window, piece):

    score = 0

    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    # winning
    if window.count(piece) == 4:
        score += 100

    # 3 connected
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 10

    # 2 connected
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 4

    # block opponent
    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 80

    return score


# =========================================================
# HEURISTIC 1
# Balanced Heuristic
# =========================================================
def evaluate_board(board):

    # ================= WIN CONDITIONS =================
    if check_win(board, AI_PIECE):
        return 100000

    if check_win(board, PLAYER_PIECE):
        return -100000

    score = 0

    # ================= CENTER CONTROL =================
    center_col = COLS // 2

    center_array = [board[r][center_col] for r in range(ROWS)]

    center_count = center_array.count(AI_PIECE)

    score += center_count * 6

    # ================= HORIZONTAL =================
    for r in range(ROWS):

        row = board[r]

        for c in range(COLS - 3):

            window = row[c:c+4]

            score += evaluate_window(window, AI_PIECE)

    # ================= VERTICAL =================
    for c in range(COLS):

        col = [board[r][c] for r in range(ROWS)]

        for r in range(ROWS - 3):

            window = col[r:r+4]

            score += evaluate_window(window, AI_PIECE)

    # ================= POSITIVE DIAGONAL =================
    for r in range(ROWS - 3):

        for c in range(COLS - 3):

            window = [board[r+i][c+i] for i in range(4)]

            score += evaluate_window(window, AI_PIECE)

    # ================= NEGATIVE DIAGONAL =================
    for r in range(3, ROWS):

        for c in range(COLS - 3):

            window = [board[r-i][c+i] for i in range(4)]

            score += evaluate_window(window, AI_PIECE)

    return score


# =========================================================
# HEURISTIC 2
# More Aggressive Heuristic
# =========================================================
def evaluate_board_v2(board):

    # ================= WIN CONDITIONS =================
    if check_win(board, AI_PIECE):
        return 100000

    if check_win(board, PLAYER_PIECE):
        return -100000

    score = 0

    # ================= STRONG CENTER CONTROL =================
    center_col = COLS // 2

    center_array = [board[r][center_col] for r in range(ROWS)]

    score += center_array.count(AI_PIECE) * 10

    # ================= HORIZONTAL =================
    for r in range(ROWS):

        row = board[r]

        for c in range(COLS - 3):

            window = row[c:c+4]

            # aggressive scoring
            if window.count(AI_PIECE) == 4:
                score += 200

            elif window.count(AI_PIECE) == 3 and window.count(0) == 1:
                score += 25

            elif window.count(AI_PIECE) == 2 and window.count(0) == 2:
                score += 8

            # stronger defense
            if window.count(PLAYER_PIECE) == 3 and window.count(0) == 1:
                score -= 120

    # ================= VERTICAL =================
    for c in range(COLS):

        col = [board[r][c] for r in range(ROWS)]

        for r in range(ROWS - 3):

            window = col[r:r+4]

            score += evaluate_window(window, AI_PIECE)

    # ================= POSITIVE DIAGONAL =================
    for r in range(ROWS - 3):

        for c in range(COLS - 3):

            window = [board[r+i][c+i] for i in range(4)]

            score += evaluate_window(window, AI_PIECE)

    # ================= NEGATIVE DIAGONAL =================
    for r in range(3, ROWS):

        for c in range(COLS - 3):

            window = [board[r-i][c+i] for i in range(4)]

            score += evaluate_window(window, AI_PIECE)

    return score


# =========================================================
# PLAYER BOARD EVALUATION
# (used only for GUI display)
# =========================================================
def evaluate_board_player(board):

    if check_win(board, PLAYER_PIECE):
        return 100000

    if check_win(board, AI_PIECE):
        return -100000

    score = 0

    center_col = COLS // 2

    center_array = [board[r][center_col] for r in range(ROWS)]

    center_count = center_array.count(PLAYER_PIECE)

    score += center_count * 6

    # horizontal
    for r in range(ROWS):

        row = board[r]

        for c in range(COLS - 3):

            window = row[c:c+4]

            score += evaluate_window(window, PLAYER_PIECE)

    # vertical
    for c in range(COLS):

        col = [board[r][c] for r in range(ROWS)]

        for r in range(ROWS - 3):

            window = col[r:r+4]

            score += evaluate_window(window, PLAYER_PIECE)

    # positive diagonal
    for r in range(ROWS - 3):

        for c in range(COLS - 3):

            window = [board[r+i][c+i] for i in range(4)]

            score += evaluate_window(window, PLAYER_PIECE)

    # negative diagonal
    for r in range(3, ROWS):

        for c in range(COLS - 3):

            window = [board[r-i][c+i] for i in range(4)]

            score += evaluate_window(window, PLAYER_PIECE)

    return score