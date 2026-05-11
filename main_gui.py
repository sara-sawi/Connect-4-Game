"""
main_gui.py  ←  RUN THIS FILE
Connect Four AI — Main GUI Entry Point
"""

import tkinter as tk
import os

# ── PIL ───────────────────────────────────────────────────────────────────────
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ── pygame ────────────────────────────────────────────────────────────────────
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# ── game logic ────────────────────────────────────────────────────────────────
from game_logic import (
    create_board, drop_piece, is_valid_location,
    get_next_open_row, check_win, randomize_board, ROWS, COLS
)
from minimax import minimax, get_valid_locations, nodes_explored, move_scores, reset_stats
from alpha_beta import alpha_beta
from evaluation import (
    evaluate_board,
    evaluate_board_v2,
    evaluate_board_player
)

# ─────────────────────────────────────────────────────────────────────────────
#  SOUND MANAGER
# ─────────────────────────────────────────────────────────────────────────────
class SoundManager:
    def __init__(self):
        self._ready        = False
        self._music_loaded = False
        self._click_sound  = None
        if not PYGAME_AVAILABLE:
            return
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            self._ready = True
        except Exception as e:
            print(f"[Sound] mixer init failed: {e}")
            return
        self._load_assets()

    def _load_assets(self):
        base = os.path.dirname(os.path.abspath(__file__))

        for fname in ("bg_music.ogg", "bg_music.wav", "bg_music.mp3"):
            p = os.path.join(base, fname)
            if os.path.exists(p):
                try:
                    pygame.mixer.music.load(p)
                    pygame.mixer.music.set_volume(0.30)
                    self._music_loaded = True
                    print(f"[Sound] music loaded: {fname}")
                    break
                except Exception as e:
                    print(f"[Sound] failed to load {fname}: {e}")

        for fname in ("click.wav", "click.ogg"):
            p = os.path.join(base, fname)
            if os.path.exists(p):
                try:
                    self._click_sound = pygame.mixer.Sound(p)
                    self._click_sound.set_volume(0.65)
                    print(f"[Sound] click loaded: {fname}")
                    break
                except Exception as e:
                    print(f"[Sound] failed to load {fname}: {e}")

    def start_music(self):
        if not self._ready:
            print("[Sound] not ready")
            return
        if not self._music_loaded:
            print("[Sound] no music file loaded")
            return
        try:
            pygame.mixer.music.play(loops=-1)
            print("[Sound] music started")
        except Exception as e:
            print(f"[Sound] music play error: {e}")

    def play_click(self):
        if self._ready and self._click_sound:
            try:
                self._click_sound.play()
            except Exception as e:
                print(f"[Sound] click error: {e}")

    def play_drop(self):
        self.play_click()

    def play_win(self):
        if not (self._ready and self._click_sound):
            return
        try:
            self._click_sound.play()
            import threading, time
            def _delayed():
                time.sleep(0.18)
                try:
                    self._click_sound.play()
                except Exception:
                    pass
            threading.Thread(target=_delayed, daemon=True).start()
        except Exception as e:
            print(f"[Sound] win sound error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER — winning cells
# ─────────────────────────────────────────────────────────────────────────────
def get_winning_cells(board, player):
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c+i] == player for i in range(4)):
                return [(r, c+i) for i in range(4)]
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r+i][c] == player for i in range(4)):
                return [(r+i, c) for i in range(4)]
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r-i][c+i] == player for i in range(4)):
                return [(r-i, c+i) for i in range(4)]
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == player for i in range(4)):
                return [(r+i, c+i) for i in range(4)]
    return []


# ─────────────────────────────────────────────────────────────────────────────
#  GAME SCREEN
# ─────────────────────────────────────────────────────────────────────────────
class GameScreen:
    BG           = "#0a0a1a"
    BOARD_BG     = "#0d2060"
    BOARD_BORDER = "#1a3aaa"
    EMPTY_COLOR  = "#060618"
    P1_COLOR     = "#e63950"
    P2_COLOR     = "#f7df00"
    TOP_BAR_H    = 60
    INFO_BAR_H   = 38

    def __init__(self, root, settings, sound_manager=None, on_menu=None):
        self.root           = root
        self.settings       = settings
        self.sound_manager  = sound_manager
        self.on_menu        = on_menu
        self._after_ids     = []
        self._overlay_frame = None

        # AI Visual Feedback
        self.nodes_explored = 0
        self.pruned_nodes   = 0
        self.ai_best_move   = "-"
        self.decision_time  = 0
        self.move_scores    = {}

        # win counts
        self.score_p1 = settings.get("score_p1", 0)
        self.score_ai = settings.get("score_ai", 0)

        # animation
        self._anim_active   = False
        self._anim_col      = -1
        self._anim_player   = 1
        self._anim_y        = 0.0
        self._anim_target   = 0
        self._anim_speed    = 0.0
        self._anim_callback = None

        # win highlight
        self._winning_cells   = []
        self._highlight_on    = False
        self._highlight_count = 0

        self.frame = tk.Frame(root, bg=self.BG)
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.board = create_board()
        if settings.get("board") == "random":
            randomize_board(self.board, moves=12)

        self.current_player = 1
        self.game_over      = False
        self.hover_col      = -1

        self._build_ui()
        self.canvas.bind("<Configure>", self._on_resize)

    # ── geometry ──────────────────────────────────────────────────────────────
    def _geometry(self):
        w         = self.canvas.winfo_width()
        h         = self.canvas.winfo_height()
        top_space = 80
        cell      = max(min(w // COLS, (h - top_space) // ROWS), 40)
        radius    = int(cell * 0.38)
        board_w   = COLS * cell
        board_h   = ROWS * cell
        off_x     = (w - board_w) // 2
        off_y     = (h - board_h) // 2 + 20
        return cell, radius, off_x, off_y

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.root.update()

        # ── top bar ───────────────────────────────────────────────────────────
        top = tk.Frame(self.frame, bg="#05051a", height=self.TOP_BAR_H)
        top.pack(fill="x")
        top.pack_propagate(False)

        back = tk.Canvas(top, width=110, height=36,
                         bg="#05051a", highlightthickness=0)
        back.place(x=12, rely=0.5, anchor="w")
        back.create_rectangle(2, 2, 108, 34, fill="#1a1a44",
                               outline="#5555cc", width=2)
        back.create_text(55, 18, text="◀  MENU",
                         font=("Impact", 12), fill="#ffffff")
        back.bind("<Button-1>", lambda _: self._back_to_menu())
        back.bind("<Enter>",    lambda _: back.itemconfig(2, fill="#2a2a66"))
        back.bind("<Leave>",    lambda _: back.itemconfig(2, fill="#1a1a44"))

        tk.Label(top, text="CONNECT  FOUR",
                 font=("Impact", 26, "bold"),
                 fg="#ffffff", bg="#05051a").place(relx=0.5, rely=0.5, anchor="center")

        self.status_var = tk.StringVar(value="YOUR TURN  🔴")
        tk.Label(top, textvariable=self.status_var,
                 font=("Courier", 11, "bold"),
                 fg="#f7df00", bg="#05051a").place(relx=0.80, rely=0.5, anchor="center")

        tk.Frame(self.frame, height=2, bg="#111166").pack(fill="x")

        # ── score bar (height=56 to fit 2 rows) ───────────────────────────────
        score_bar = tk.Frame(self.frame, bg="#08082a", height=56)
        score_bar.pack(fill="x")
        score_bar.pack_propagate(False)

        # ── YOU side ──────────────────────────────────────────────────────────
        p1_block = tk.Frame(score_bar, bg="#08082a")
        p1_block.place(relx=0.18, rely=0.35, anchor="center")

        tk.Label(p1_block, text="🔴  YOU",
                 font=("Impact", 13), fg=self.P1_COLOR,
                 bg="#08082a").pack(side="left", padx=(0, 6))

        self.score_p1_var = tk.StringVar(value=str(self.score_p1))
        tk.Label(p1_block, textvariable=self.score_p1_var,
                 font=("Impact", 22), fg=self.P1_COLOR,
                 bg="#08082a").pack(side="left")

        # Player board score (small, below)
        self.p1_board_score_var = tk.StringVar(value="Board Score: 0")
        tk.Label(score_bar, textvariable=self.p1_board_score_var,
                 font=("Courier", 9, "bold"),
                 fg="#ff8899", bg="#08082a").place(relx=0.18, rely=0.80, anchor="center")

        # ── VS ────────────────────────────────────────────────────────────────
        tk.Label(score_bar, text="VS",
                 font=("Impact", 12), fg="#333366",
                 bg="#08082a").place(relx=0.5, rely=0.5, anchor="center")

        # ── AI side ───────────────────────────────────────────────────────────
        ai_block = tk.Frame(score_bar, bg="#08082a")
        ai_block.place(relx=0.78, rely=0.35, anchor="center")

        self.score_ai_var = tk.StringVar(value=str(self.score_ai))
        tk.Label(ai_block, textvariable=self.score_ai_var,
                 font=("Impact", 22), fg=self.P2_COLOR,
                 bg="#08082a").pack(side="left")

        tk.Label(ai_block, text="AI  🟡",
                 font=("Impact", 13), fg=self.P2_COLOR,
                 bg="#08082a").pack(side="left", padx=(6, 0))

        # AI board score (small, below)
        self.ai_board_score_var = tk.StringVar(value="Board Score: 0")
        tk.Label(score_bar, textvariable=self.ai_board_score_var,
                 font=("Courier", 9, "bold"),
                 fg="#aaee00", bg="#08082a").place(relx=0.78, rely=0.80, anchor="center")

        tk.Frame(self.frame, height=1, bg="#111155").pack(fill="x")

        # ── info bar (bottom) ─────────────────────────────────────────────────
        info = tk.Frame(self.frame, bg="#0c0c2a", height=self.INFO_BAR_H)
        info.pack(fill="x", side="bottom")
        info.pack_propagate(False)
        ai_name    = self.settings.get("ai", "minimax").upper().replace("_", "-")
        depth_val  = self.settings.get("depth")
        depth_str  = f"  |  Depth {depth_val}" if depth_val else ""
        board_str  = self.settings.get("board", "empty").upper()
        # ✅ Show heuristic in info bar
        heuristic_label = self.settings.get("heuristic", "h1").upper()
        tk.Label(info,
                 text=f"AI: {ai_name}{depth_str}      Board: {board_str}      Heuristic: {heuristic_label}",
                 font=("Courier", 10), fg="#7777bb", bg="#0c0c2a").pack(
                 side="left", padx=16)

        # ── board canvas ──────────────────────────────────────────────────────
        self.canvas = tk.Canvas(self.frame, bg=self.BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # ── AI INFO PANEL ─────────────────────────────────────────────────────
        self.ai_info_var = tk.StringVar()
        self.ai_info_label = tk.Label(
            self.frame,
            textvariable=self.ai_info_var,
            font=("Courier", 10, "bold"),
            fg="#00ffcc",
            bg="#0a0a1a",
            justify="left",
            anchor="nw"
        )
        self.ai_info_label.place(x=15, y=150)

        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>",   self._on_hover)
        self.canvas.bind("<Leave>",    self._on_leave)

        self._draw_board()

    # ── resize ────────────────────────────────────────────────────────────────
    def _on_resize(self, event):
        self._draw_board()
        if self._overlay_frame and self._overlay_frame.winfo_exists():
            self._overlay_frame.place(relx=0.5, rely=0.5, anchor="center")

    # ── board scores update ───────────────────────────────────────────────────
    def _update_board_scores(self):
        """
        Calculates score for Player and AI separately after each move.
        ✅ FIX: Uses the heuristic chosen by the user (H1 or H2) for AI score.
        """
        # ── AI board score ────────────────────────────────────────────────────
        try:
            heuristic_type = self.settings.get("heuristic", "h1")
            if heuristic_type == "h1":
                ai_s = evaluate_board(self.board)
            else:
                ai_s = evaluate_board_v2(self.board)
            self.ai_board_score_var.set(f"Board Score: {ai_s:+d}")
        except Exception as e:
            print(f"[Score] AI error: {e}")

        # ── Player board score ────────────────────────────────────────────────
        try:
            p1_s = evaluate_board_player(self.board)
            self.p1_board_score_var.set(f"Board Score: {p1_s:+d}")
        except Exception as e:
            print(f"[Score] Player error: {e}")

    # ── AI info panel update ──────────────────────────────────────────────────
    def _update_ai_info(self):
        nodes      = getattr(self, "nodes_explored", 0)
        pruned     = getattr(self, "pruned_nodes", 0)
        best       = getattr(self, "ai_best_move", "-")
        time_taken = getattr(self, "decision_time", 0)

        if self.move_scores:
            scores_text = "\n".join(
                [f"Col {c}: {s}" for c, s in sorted(self.move_scores.items())]
            )
        else:
            scores_text = "No move analysis yet"

        self.ai_info_var.set(
            "AI ANALYSIS\n"
            "────────────────\n"
            f"Best Move : {best}\n"
            f"Nodes     : {nodes}\n"
            f"Pruned    : {pruned}\n"
            f"Depth     : {self.settings.get('depth', 4)}\n"
            f"Time      : {time_taken}s\n\n"
            "MOVE SCORES\n"
            "────────────────\n"
            f"{scores_text}"
        )

    # ── thinking animation ────────────────────────────────────────────────────
    def _animate_thinking(self):
        if self.current_player != 2 or self.game_over:
            return
        dots = "." * (self._thinking_dots % 4)
        self.status_var.set(f"AI THINKING{dots} 🟡")
        self._thinking_dots += 1
        thinking_id = self.root.after(400, self._animate_thinking)
        self._after_ids.append(thinking_id)

    # ── drawing helpers ───────────────────────────────────────────────────────
    def _oval(self, cx, cy, r, fill, outline="#ffffff", width=2, stipple=""):
        kw = dict(fill=fill, outline=outline, width=width, tags="board")
        if stipple:
            kw["stipple"] = stipple
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, **kw)

    def _draw_piece(self, cx, cy, r, color, stipple=""):
        self._oval(cx, cy, r, "#000000", outline="", width=0, stipple="gray25")
        self._oval(cx, cy, r, color, outline="#ffffff", width=2, stipple=stipple)
        if not stipple:
            self._oval(cx-r*0.2, cy-r*0.3, r*0.3,
                       "#ffffff", outline="", width=0, stipple="gray25")

    # ── board drawing ─────────────────────────────────────────────────────────
    def _draw_board(self, anim_col=-1, anim_row_f=-1.0, anim_player=1):
        self.canvas.delete("board")
        cell, radius, off_x, off_y = self._geometry()

        self.canvas.create_rectangle(
            off_x, off_y,
            off_x + COLS * cell, off_y + ROWS * cell,
            fill=self.BOARD_BG, outline=self.BOARD_BORDER,
            width=3, tags="board")

        # Highlight AI best move column
        if self.current_player == 2 and self.ai_best_move != "-":
            x1 = off_x + self.ai_best_move * cell
            self.canvas.create_rectangle(
                x1, off_y, x1 + cell, off_y + ROWS * cell,
                outline="#00ffcc", width=4, tags="board")

        if (0 <= self.hover_col < COLS
                and not self.game_over
                and not self._anim_active
                and self.current_player == 1):
            x1 = off_x + self.hover_col * cell
            self.canvas.create_rectangle(
                x1, off_y, x1 + cell, off_y + ROWS * cell,
                fill="#152570", outline="", tags="board")

        if not self.game_over and self.current_player == 1:
            if self._anim_active:
                ghost_col = self._anim_col
            elif 0 <= self.hover_col < COLS:
                ghost_col = self.hover_col
            else:
                ghost_col = -1

            if ghost_col >= 0:
                gx = off_x + ghost_col * cell + cell // 2
                gy = off_y - cell // 3
                gr = radius - 4
                self._oval(gx, gy, gr+2, "#000000",
                           outline="", width=0, stipple="gray25")
                self._oval(gx, gy, gr, self.P1_COLOR,
                           outline="#ffffff", width=2, stipple="gray50")

        for row in range(ROWS):
            for col in range(COLS):
                cx  = off_x + col * cell + cell // 2
                cy  = off_y + row * cell + cell // 2
                val = self.board[row][col]
                is_winner = (row, col) in self._winning_cells

                if is_winner and self._highlight_on:
                    r_draw = int(radius * 1.15)
                    self._oval(cx, cy, r_draw+3, "#000000",
                               outline="", width=0, stipple="gray25")
                    self._oval(cx, cy, r_draw, "#ffffff",
                               outline="#ffffff", width=3)
                else:
                    color = (self.EMPTY_COLOR, self.P1_COLOR, self.P2_COLOR)[val]
                    out   = "#ffffff" if val > 0 else "#111144"
                    self._draw_piece(cx, cy, radius, color) \
                        if val > 0 else \
                        self._oval(cx, cy, radius, color, outline=out, width=1)

        if anim_col >= 0 and anim_row_f >= -1.0:
            ax = off_x + anim_col * cell + cell // 2
            ay = off_y + anim_row_f * cell + cell // 2
            pc = self.P1_COLOR if anim_player == 1 else self.P2_COLOR
            self._draw_piece(ax, ay, radius, pc)

    # ── drop animation ────────────────────────────────────────────────────────
    def _start_drop_animation(self, col, player, on_finish):
        target_row = get_next_open_row(self.board, col)
        if target_row is None:
            on_finish()
            return
        self._anim_active   = True
        self._anim_col      = col
        self._anim_player   = player
        self._anim_y        = -1.0
        self._anim_target   = target_row
        self._anim_speed    = 0.3
        self._anim_callback = on_finish
        self._animate_drop()

    def _animate_drop(self):
        self._anim_speed = min(self._anim_speed * 1.35 + 0.15, 3.5)
        self._anim_y    += self._anim_speed

        if self._anim_y >= self._anim_target:
            self._anim_active = False
            drop_piece(self.board, self._anim_col, self._anim_player)
            if self.sound_manager:
                self.sound_manager.play_drop()
            self._draw_board()
            cb = self._anim_callback
            self._anim_callback = None
            if cb:
                cb()
            return

        self._draw_board(anim_col=self._anim_col,
                         anim_row_f=self._anim_y,
                         anim_player=self._anim_player)
        self._after_ids.append(self.root.after(16, self._animate_drop))

    # ── win blink ─────────────────────────────────────────────────────────────
    def _start_win_highlight(self, cells, on_finish):
        self._winning_cells   = cells
        self._highlight_on    = False
        self._highlight_count = 0
        self._blink_highlight(on_finish)

    def _blink_highlight(self, on_finish):
        self._highlight_on = not self._highlight_on
        self._draw_board()
        self._highlight_count += 1
        if self._highlight_count < 8:
            self._after_ids.append(
                self.root.after(200, lambda: self._blink_highlight(on_finish)))
        else:
            self._highlight_on = True
            self._draw_board()
            if on_finish:
                on_finish()

    # ── input ─────────────────────────────────────────────────────────────────
    def _on_hover(self, event):
        if self._anim_active or self.game_over or self.current_player != 1:
            return
        col = self._pixel_to_col(event.x)
        if col != self.hover_col:
            self.hover_col = col
            self._draw_board()

    def _on_leave(self, _event):
        if self.hover_col != -1:
            self.hover_col = -1
            self._draw_board()

    def _on_click(self, event):
        if self.game_over or self.current_player != 1 or self._anim_active:
            return
        col = self._pixel_to_col(event.x)
        if not (0 <= col < COLS) or not is_valid_location(self.board, col):
            return
        self.hover_col = col
        self._start_drop_animation(col, 1, self._after_player_drop)

    def _after_player_drop(self):
        self._update_board_scores()
        self.hover_col = -1
        if check_win(self.board, 1):
            cells = get_winning_cells(self.board, 1)
            self.score_p1 += 1
            self.score_p1_var.set(str(self.score_p1))
            if self.sound_manager:
                self.sound_manager.play_win()
            self._start_win_highlight(cells,
                on_finish=lambda: self._end_game("YOU WIN! 🎉", "#e63950"))
            return
        if not get_valid_locations(self.board):
            self._end_game("IT'S A DRAW!", "#8888ff")
            return
        self.current_player = 2
        self._thinking_dots = 0
        self._animate_thinking()
        self._after_ids.append(self.root.after(200, self._ai_turn))

    # ── AI turn ───────────────────────────────────────────────────────────────
    def _ai_turn(self):
        self.status_var.set("AI IS CHOOSING MOVE... 🟡")
        ai    = self.settings.get("ai", "minimax")
        depth = self.settings.get("depth", 4) or 4
        col   = None

        import time
        start_time = time.time()
        reset_stats()

        # ✅ HEURISTIC SELECTION — based on user's menu choice
        heuristic_type = self.settings.get("heuristic", "h1")
        if heuristic_type == "h1":
            heuristic_func = evaluate_board
        else:
            heuristic_func = evaluate_board_v2

        # ✅ AI ALGORITHM SELECTION
        if ai == "minimax":
            col, _ = minimax(
                self.board,
                depth,
                True,
                heuristic_func
            )
        elif ai == "alpha_beta":
            col, _ = alpha_beta(
                self.board,
                depth,
                float("-inf"),
                float("inf"),
                True,
                heuristic_func
            )

        end_time = time.time()
        self.decision_time = round(end_time - start_time, 2)

        if col is None or not is_valid_location(self.board, col):
            valid = get_valid_locations(self.board)
            col   = valid[0] if valid else None

        if col is None:
            self._end_game("IT'S A DRAW!", "#8888ff")
            return

        self.ai_best_move = col

        from minimax import nodes_explored as mm_nodes, move_scores as mm_scores
        from alpha_beta import nodes_explored as ab_nodes, move_scores as ab_scores, pruned_nodes as ab_pruned

        if ai == "alpha_beta":
            self.nodes_explored = ab_nodes
            self.move_scores    = ab_scores.copy()
            self.pruned_nodes   = ab_pruned
        else:
            self.nodes_explored = mm_nodes
            self.move_scores    = mm_scores.copy()
            self.pruned_nodes   = 0

        self._update_ai_info()
        self._start_drop_animation(col, 2, self._after_ai_drop)

    def _after_ai_drop(self):
        self._update_board_scores()
        self.status_var.set("YOUR TURN 🔴")
        if check_win(self.board, 2):
            cells = get_winning_cells(self.board, 2)
            self.score_ai += 1
            self.score_ai_var.set(str(self.score_ai))
            if self.sound_manager:
                self.sound_manager.play_win()
            self._start_win_highlight(cells,
                on_finish=lambda: self._end_game("AI WINS! 🤖", "#f7df00"))
            return
        if not get_valid_locations(self.board):
            self._end_game("IT'S A DRAW!", "#8888ff")
            return
        self.current_player = 1
        self.status_var.set("YOUR TURN  🔴")

    # ── helpers ───────────────────────────────────────────────────────────────
    def _pixel_to_col(self, x):
        cell, _, off_x, _ = self._geometry()
        return int((x - off_x) // cell)

    # ── end game ──────────────────────────────────────────────────────────────
    def _end_game(self, msg, accent):
        self.game_over = True
        self.status_var.set(msg)

        ov = tk.Frame(self.frame, bg="#09091f",
                      highlightbackground=accent,
                      highlightthickness=3)
        self._overlay_frame = ov

        tk.Label(ov, text=msg,
                 font=("Impact", 46, "bold"),
                 fg=accent, bg="#09091f").pack(padx=40, pady=(30, 4))

        score_txt = f"YOU  {self.score_p1}  —  {self.score_ai}  AI"
        tk.Label(ov, text=score_txt,
                 font=("Courier", 14, "bold"),
                 fg="#aaaaee", bg="#09091f").pack(pady=(0, 4))

        # ✅ FIX: Use selected heuristic for final AI board score in end game
        try:
            final_p1 = evaluate_board_player(self.board)
            heuristic_type = self.settings.get("heuristic", "h1")
            if heuristic_type == "h1":
                final_ai = evaluate_board(self.board)
            else:
                final_ai = evaluate_board_v2(self.board)

            tk.Label(ov,
                     text=f"🔴 Player Score: {final_p1:+d}",
                     font=("Courier", 11, "bold"),
                     fg="#ff8899", bg="#09091f").pack(pady=(0, 2))
            tk.Label(ov,
                     text=f"🟡 AI Score ({heuristic_type.upper()}): {final_ai:+d}",
                     font=("Courier", 11, "bold"),
                     fg="#aaee00", bg="#09091f").pack(pady=(0, 4))
        except Exception:
            pass

        tk.Label(ov, text="─────────────────────",
                 font=("Courier", 10), fg="#333366", bg="#09091f").pack()

        btn = tk.Label(ov, text="▶ PLAY AGAIN",
                       font=("Impact", 18),
                       fg="#ffffff", bg="#1a1a44",
                       padx=20, pady=10,
                       cursor="hand2")
        btn.pack(pady=(10, 20))
        btn.bind("<Enter>",    lambda e: btn.config(bg="#2a2a66"))
        btn.bind("<Leave>",    lambda e: btn.config(bg="#1a1a44"))
        btn.bind("<Button-1>", lambda e: self._play_again())

        ov.place(relx=0.5, rely=0.5, anchor="center")
        ov.lift()

    def _back_to_menu(self):
        if self.sound_manager:
            self.sound_manager.play_click()
        for aid in self._after_ids:
            try: self.root.after_cancel(aid)
            except Exception: pass
        if self._overlay_frame and self._overlay_frame.winfo_exists():
            self._overlay_frame.destroy()
        self.frame.destroy()
        if self.on_menu:
            self.on_menu()

    def _play_again(self):
        self.board = create_board()
        if self.settings.get("board") == "random":
            randomize_board(self.board, moves=12)
        self.current_player = 1
        self.game_over      = False
        self._winning_cells = []
        self.hover_col      = -1
        if self._overlay_frame and self._overlay_frame.winfo_exists():
            self._overlay_frame.destroy()
        self.status_var.set("YOUR TURN  🔴")
        self.p1_board_score_var.set("Board Score: 0")
        self.ai_board_score_var.set("Board Score: 0")
        self._draw_board()


# ─────────────────────────────────────────────────────────────────────────────
#  APP CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────
class ConnectFourApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connect Four AI")
        self.root.geometry("900x720")
        self.root.minsize(800, 640)
        self.root.configure(bg="#0a0a1a")
        self.root.resizable(True, True)

        self.sound = SoundManager()
        self.sound.start_music()

        self._score_p1     = 0
        self._score_ai     = 0
        self._current_game = None

        self._show_splash()

    def _show_splash(self):
        from splash_screen import SplashScreen
        SplashScreen(self.root,
                     on_complete=self._show_menu,
                     sound_manager=self.sound)

    def _show_menu(self):
        from menu_screen import MenuScreen
        MenuScreen(self.root,
                   on_start=self._show_game,
                   sound_manager=self.sound)

    def _show_game(self, settings):
        # ✅ Ensure heuristic key always exists (fallback to "h1")
        if "heuristic" not in settings:
            settings["heuristic"] = "h1"
        settings["score_p1"] = self._score_p1
        settings["score_ai"] = self._score_ai
        self._current_game = GameScreen(
            self.root,
            settings=settings,
            sound_manager=self.sound,
            on_menu=self._on_back_to_menu)

    def _on_back_to_menu(self):
        if self._current_game:
            self._score_p1 = self._current_game.score_p1
            self._score_ai = self._current_game.score_ai
        self._show_menu()

    def run(self):
        self.root.mainloop()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ConnectFourApp()
    app.run()