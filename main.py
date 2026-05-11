from game_logic import (
    create_board,
    print_board,
    drop_piece,
    is_valid_location,
    check_win,
    randomize_board,
    COLS
)

from minimax import minimax
from heuristic_ai import heuristic_move
from alpha_beta import alpha_beta


def main():

    # ================= MODE SELECTION =================
    print("Choose game mode:")
    print("1 - Normal (Empty board)")
    print("2 - Random (Test board)")

    mode = input("Enter choice (1 or 2): ")

    # ================= AI SELECTION =================
    print("\nChoose AI type:")
    print("1 - Minimax AI")
    print("2 - Heuristic AI")
    print("3 - Alpha-Beta AI")

    ai_choice = input("Enter choice (1, 2, or 3): ")

    # ================= DIFFICULTY =================
    depth = None

    if ai_choice in ["1", "3"]:   # Minimax أو Alpha-Beta
        print("\nChoose difficulty level:")
        print("1 - Easy")
        print("2 - Medium")
        print("3 - Hard")

        difficulty = input("Enter choice (1, 2, or 3): ")

        if difficulty == "1":
            depth = 2
        elif difficulty == "2":
            depth = 4
        elif difficulty == "3":
            depth = 6
        else:
            print("Invalid choice, defaulting to Medium.")
            depth = 4
    else:
        print("Heuristic AI does not use difficulty levels.")

    # ================= BOARD SETUP =================
    board = create_board()

    if mode == "2":
        randomize_board(board, moves=12)

    print("\nStarting Board:")
    print_board(board)

    # ================= GAME LOOP =================
    turn = 0
    game_over = False

    while not game_over:

        # ================= HUMAN =================
        if turn == 0:
            try:
                col = int(input("Player 1, choose a column (0-6): "))
            except ValueError:
                print("Enter a valid number!")
                continue

        # ================= AI =================
        else:
            print("AI is thinking...")

            if ai_choice == "1":
                col, score = minimax(board, depth, True)

            elif ai_choice == "2":
                col, score = heuristic_move(board)

            elif ai_choice == "3":
                col, score = alpha_beta(
                    board,
                    depth,
                    -float("inf"),
                    float("inf"),
                    True
                )

            else:
                print("Invalid AI choice, using Heuristic by default.")
                col, score = heuristic_move(board)

        # ================= VALIDATION =================
        if 0 <= col < COLS:

            if is_valid_location(board, col):

                drop_piece(board, col, turn + 1)
                print_board(board)

                if check_win(board, turn + 1):
                    if turn == 0:
                        print("🎉 Player wins!")
                    else:
                        print("🤖 AI wins!")
                    game_over = True

                turn = (turn + 1) % 2

            else:
                print("Column full!")

        else:
            print("Invalid column!")


if __name__ == "__main__":
    main()
