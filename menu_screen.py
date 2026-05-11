"""
menu_screen.py  —  Connect Four AI  |  Main Menu
Colours: blue = board, yellow = AI, red = difficulty + START
No default selections — user must pick all options before START unlocks.
Difficulty section always appears ABOVE the START button.
Heuristic hides difficulty; switching away restores it (and clears selection).
"""

import tkinter as tk
import math


# ─────────────────────────────────────────────────────────────────────────────
#  FONT RESOLVER
# ─────────────────────────────────────────────────────────────────────────────
def _best_font(root, candidates):
    try:
        import tkinter.font as tkf
        avail = set(tkf.families(root))
    except Exception:
        avail = set()
    for spec in candidates:
        if spec[0] in avail:
            return spec
    return candidates[-1]


# ─────────────────────────────────────────────────────────────────────────────
#  PALETTE
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "bg"             : "#08081e",
    "panel_bg"       : "#0c0c24",
    "panel_border"   : "#2a2a60",
    "topbar_bg"      : "#06061a",
    "topbar_line"    : "#2244cc",
    "divider"        : "#1a1a40",
    "sec_blue"       : "#4477ff",
    "sec_yellow"     : "#d4aa00",
    "sec_red"        : "#e8304a",
    "sec_label"      : "#7888cc",
    "sec_line"       : "#1a1a3e",
    "opt_bg"         : "#0e0e28",
    "opt_border"     : "#2a2a70",
    "opt_text"       : "#8899ee",
    "opt_hov_bg"     : "#141430",
    "opt_hov_brd"    : "#3344bb",
    "opt_hov_tx"     : "#aabbff",
    "sel_blue_bg"    : "#060e28",
    "sel_blue_brd"   : "#3366ff",
    "sel_blue_tx"    : "#7799ff",
    "sel_yel_bg"     : "#141000",
    "sel_yel_brd"    : "#d4aa00",
    "sel_yel_tx"     : "#f0cc00",
    "sel_red_bg"     : "#1a0608",
    "sel_red_brd"    : "#e8304a",
    "sel_red_tx"     : "#ff5566",
    "start_lock_bg"  : "#09091e",
    "start_lock_brd" : "#2a2a70",
    "start_lock_tx"  : "#6670bb",
    "start_bg"       : "#0a0414",
    "start_brd"      : "#e8304a",
    "start_tx"       : "#ff4466",
    "start_hov_bg"   : "#180510",
    "start_hov_brd"  : "#ff5566",
    "start_hov_tx"   : "#ff7788",
    "title_white"    : "#dde4ff",
    "title_yellow"   : "#f5d800",
    "title_ai"       : "#8899ee",
    "hint_idle"      : "#5055aa",
    "hint_ready"     : "#3a6020",
    "subtitle"       : "#6070bb",
}


# ─────────────────────────────────────────────────────────────────────────────
#  OPTION BUTTON
# ─────────────────────────────────────────────────────────────────────────────
class OptionButton(tk.Canvas):
    SEL_PALETTES = {
        "blue"  : ("sel_blue_bg",  "sel_blue_brd",  "sel_blue_tx"),
        "yellow": ("sel_yel_bg",   "sel_yel_brd",   "sel_yel_tx"),
        "red"   : ("sel_red_bg",   "sel_red_brd",   "sel_red_tx"),
    }

    def __init__(self, parent, text, icon="",
                 width=175, height=48,
                 sel_color="blue",
                 on_select=None, sound_manager=None, **kwargs):
        bg = parent.cget("bg") if hasattr(parent, "cget") else C["bg"]
        super().__init__(parent, width=width, height=height,
                         bg=bg, highlightthickness=0, **kwargs)
        self.text          = text
        self.icon          = icon
        self.W             = width
        self.H             = height
        self.sel_color     = sel_color
        self.on_select     = on_select
        self.sound_manager = sound_manager
        self._selected     = False
        self._hovered      = False
        self._btn_font     = ("Segoe UI", 11, "bold")
        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _draw(self):
        self.delete("all")
        W, H, R = self.W, self.H, 8
        if self._selected:
            kb, kbrd, ktx = self.SEL_PALETTES[self.sel_color]
            bg_c, brd_c, tx_c, bw = C[kb], C[kbrd], C[ktx], 2
        elif self._hovered:
            bg_c, brd_c, tx_c, bw = (C["opt_hov_bg"], C["opt_hov_brd"],
                                      C["opt_hov_tx"], 1)
        else:
            bg_c, brd_c, tx_c, bw = (C["opt_bg"], C["opt_border"],
                                      C["opt_text"], 1)
        self._rr(3, 3, W+1, H+1, R, fill="#000000", outline="")
        self._rr(0, 0, W-3, H-3, R, fill=bg_c,  outline="")
        self._rr(0, 0, W-3, H-3, R, fill="",    outline=brd_c, width=bw)
        if self._selected:
            _, kbrd, _ = self.SEL_PALETTES[self.sel_color]
            self.create_text(W-12, 8, text="✔",
                             font=("Arial", 7, "bold"),
                             fill=C[kbrd], anchor="center")
        label = f"{self.icon}  {self.text}" if self.icon else self.text
        self.create_text((W-3)//2, (H-3)//2, text=label,
                         font=self._btn_font, fill=tx_c, anchor="center")

    def _rr(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
               x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
               x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(pts, smooth=True, **kw)

    def select(self):
        self._selected = True;  self._hovered = False;  self._draw()

    def deselect(self):
        self._selected = False;  self._draw()

    def _on_enter(self, _):
        if not self._selected:
            self._hovered = True;  self._draw()

    def _on_leave(self, _):
        self._hovered = False
        if not self._selected:
            self._draw()

    def _on_click(self, _):
        if self.sound_manager:
            self.sound_manager.play_click()
        if self.on_select:
            self.on_select()


# ─────────────────────────────────────────────────────────────────────────────
#  OPTION GROUP  (no default)
# ─────────────────────────────────────────────────────────────────────────────
class OptionGroup:
    def __init__(self, parent, options,
                 button_w=175, button_h=48,
                 sel_color="blue",
                 sound_manager=None,
                 on_change=None,
                 icons=None,
                 btn_font=None):
        self.buttons   = {}
        self._value    = None
        self.on_change = on_change
        icons = icons or {}
        for i, (label, val) in enumerate(options):
            btn = OptionButton(parent, label, icon=icons.get(val, ""),
                               width=button_w, height=button_h,
                               sel_color=sel_color,
                               on_select=lambda v=val: self._select(v),
                               sound_manager=sound_manager)
            if btn_font:
                btn._btn_font = btn_font
                btn._draw()
            btn.grid(row=0, column=i, padx=6, pady=2)
            self.buttons[val] = btn

    def _select(self, val):
        self._value = val
        for v, btn in self.buttons.items():
            btn.select() if v == val else btn.deselect()
        if self.on_change:
            self.on_change(val)

    def get(self):    return self._value
    def is_set(self): return self._value is not None

    def clear(self):
        self._value = None
        for btn in self.buttons.values():
            btn.deselect()


# ─────────────────────────────────────────────────────────────────────────────
#  START BUTTON
# ─────────────────────────────────────────────────────────────────────────────
class StartButton(tk.Canvas):
    W, H, R = 272, 52, 10

    def __init__(self, parent, command, sound_manager=None, btn_font=None):
        bg = parent.cget("bg") if hasattr(parent, "cget") else C["bg"]
        super().__init__(parent, width=self.W, height=self.H,
                         bg=bg, highlightthickness=0)
        self.command       = command
        self.sound_manager = sound_manager
        self._locked       = True
        self._hovered      = False
        self._btn_font     = btn_font or ("Segoe UI", 12, "bold")
        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _draw(self):
        self.delete("all")
        W, H, R = self.W, self.H, self.R
        if self._locked:
            bg_c, brd_c, tx_c, bw = (C["start_lock_bg"], C["start_lock_brd"],
                                      C["start_lock_tx"], 1)
            label = "— SELECT ALL OPTIONS —"
        elif self._hovered:
            bg_c, brd_c, tx_c, bw = (C["start_hov_bg"], C["start_hov_brd"],
                                      C["start_hov_tx"], 2)
            label = "▶   START GAME"
        else:
            bg_c, brd_c, tx_c, bw = (C["start_bg"], C["start_brd"],
                                      C["start_tx"], 2)
            label = "▶   START GAME"
        self._rr(3, 3, W+1, H+1, R, fill="#000000", outline="")
        self._rr(0, 0, W-3, H-3, R, fill=bg_c, outline="")
        self._rr(0, 0, W-3, H-3, R, fill="", outline=brd_c, width=bw)
        if not self._locked:
            self._rr(1, 1, W-4, (H-3)//2, R-2,
                     fill="#ffffff", outline="", stipple="gray12")
        self.create_text((W-3)//2, (H-3)//2, text=label,
                         font=self._btn_font, fill=tx_c, anchor="center")

    def _rr(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
               x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
               x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(pts, smooth=True, **kw)

    def unlock(self):
        self._locked = False;  self._hovered = False;  self._draw()

    def lock(self):
        self._locked = True;   self._hovered = False;  self._draw()

    def _on_enter(self, _):
        if not self._locked:
            self._hovered = True;  self._draw()

    def _on_leave(self, _):
        self._hovered = False
        if not self._locked:
            self._draw()

    def _on_click(self, _):
        if self._locked:
            return
        if self.sound_manager:
            self.sound_manager.play_click()
        if self.command:
            self.command()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION LABEL
# ─────────────────────────────────────────────────────────────────────────────
def _section_label(parent, text, dot_color, bg, f_label):
    f = tk.Frame(parent, bg=bg)
    dot = tk.Canvas(f, width=8, height=8, bg=bg, highlightthickness=0)
    dot.create_oval(1, 1, 7, 7, fill=dot_color, outline="")
    dot.pack(side="left", padx=(0, 7))
    tk.Label(f, text=text, font=f_label,
             fg=C["sec_label"], bg=bg).pack(side="left")
    tk.Frame(f, height=1, bg=C["sec_line"]).pack(
        side="left", fill="x", expand=True, padx=(10, 0))
    return f


# ─────────────────────────────────────────────────────────────────────────────
#  MENU SCREEN
# ─────────────────────────────────────────────────────────────────────────────
class MenuScreen:
    BG       = C["bg"]
    PANEL_BG = C["panel_bg"]

    def __init__(self, root, on_start, sound_manager=None):
        self.root          = root
        self.on_start      = on_start
        self.sound_manager = sound_manager
        self._after_ids    = []
        self._pulse        = 0.0
        self._diff_hidden  = False
        self._heur_hidden  = False
        self._muted        = False

        # ── fonts ─────────────────────────────────────────────────────────────
        self.F_TITLE = _best_font(root, [
            ("Bahnschrift", 40, "bold"),
            ("Segoe UI",    40, "bold"),
            ("Arial Black", 38, "bold"),
            ("Arial",       38, "bold"),
        ])
        self.F_TITLE_AI = _best_font(root, [
            ("Bahnschrift", 20, "bold"),
            ("Segoe UI",    20, "bold"),
            ("Arial",       20, "bold"),
        ])
        self.F_SEC = _best_font(root, [
            ("Consolas", 9), ("Lucida Console", 9),
            ("Courier New", 9), ("Courier", 9),
        ])
        self.F_BTN = _best_font(root, [
            ("Bahnschrift", 11), ("Segoe UI", 11, "bold"), ("Arial", 11, "bold"),
        ])
        self.F_START = _best_font(root, [
            ("Bahnschrift", 12), ("Segoe UI", 12, "bold"), ("Arial", 12, "bold"),
        ])
        self.F_HINT = _best_font(root, [
            ("Consolas", 8), ("Lucida Console", 8), ("Courier", 8),
        ])
        self.F_SUB = _best_font(root, [
            ("Consolas", 9), ("Lucida Console", 9), ("Courier", 9),
        ])

        self.frame = tk.Frame(root, bg=self.BG)
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_title_bar()
        self._build_panel()
        self._animate_title()

    # ── title bar ─────────────────────────────────────────────────────────────
    def _build_title_bar(self):
        bar = tk.Frame(self.frame, bg=C["topbar_bg"], height=82)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tf = tk.Frame(bar, bg=C["topbar_bg"])
        tf.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_connect = tk.Label(tf, text="CONNECT ",
            font=self.F_TITLE, fg=C["title_white"], bg=C["topbar_bg"])
        self.lbl_connect.pack(side="left")

        self.lbl_four = tk.Label(tf, text="FOUR",
            font=self.F_TITLE, fg=C["title_yellow"], bg=C["topbar_bg"])
        self.lbl_four.pack(side="left")

        tk.Label(tf, text="  AI",
            font=self.F_TITLE_AI, fg=C["title_ai"],
            bg=C["topbar_bg"]).pack(side="left", pady=(12, 0))

        # ── sound toggle ──────────────────────────────────────────────────────
        self._snd_btn = tk.Canvas(bar, width=48, height=40,
                                   bg=C["topbar_bg"], highlightthickness=0)
        self._snd_btn.place(relx=1.0, rely=0.5, x=-16, anchor="e")
        self._snd_btn.create_rectangle(2, 2, 46, 38,
                                        fill="#1a1a44", outline="#5555cc",
                                        width=2, tags="bg")
        self._snd_btn.create_text(24, 20, text="🔊",
                                   font=("Segoe UI Emoji", 16), tags="icon")
        self._snd_btn.bind("<Button-1>", self._toggle_sound)
        self._snd_btn.bind("<Enter>",
            lambda _: self._snd_btn.itemconfig("bg", fill="#2a2a66"))
        self._snd_btn.bind("<Leave>",
            lambda _: self._snd_btn.itemconfig("bg", fill="#1a1a44"))

        tk.Frame(self.frame, height=2, bg=C["topbar_line"]).pack(fill="x")

    # ── sound toggle ──────────────────────────────────────────────────────────
    def _toggle_sound(self, _event=None):
        self._muted = not self._muted
        try:
            import pygame
            if self._muted:
                pygame.mixer.music.set_volume(0.0)
                self._snd_btn.itemconfig("icon", text="🔇")
            else:
                pygame.mixer.music.set_volume(0.30)
                self._snd_btn.itemconfig("icon", text="🔊")
        except Exception as e:
            print(f"[Sound toggle] {e}")

    # ── panel ─────────────────────────────────────────────────────────────────
    def _build_panel(self):
        P = self.PANEL_BG

        outer = tk.Frame(self.frame, bg=self.BG)
        outer.pack(fill="both", expand=True)

        card = tk.Frame(outer, bg=P,
                        highlightbackground=C["panel_border"],
                        highlightthickness=1)
        card.pack(expand=True, pady=18, padx=52, fill="both")

        self._inner = tk.Frame(card, bg=P)
        self._inner.pack(padx=30, pady=18, fill="both")
        inner = self._inner

        tk.Label(inner, text="—  M A I N   M E N U  —",
                 font=self.F_SUB, fg=C["subtitle"], bg=P).pack(pady=(0, 14))

        # ── BOARD TYPE ────────────────────────────────────────────────────────
        _section_label(inner, "BOARD TYPE", C["sec_blue"], P,
                       self.F_SEC).pack(fill="x", pady=(0, 7))
        br = tk.Frame(inner, bg=P)
        br.pack()
        self.board_group = OptionGroup(
            br,
            [("EMPTY", "empty"), ("RANDOM", "random")],
            button_w=205, button_h=48,
            sel_color="blue",
            sound_manager=self.sound_manager,
            on_change=self._on_any_change,
            icons={"empty": "◻", "random": "⊞"},
            btn_font=self.F_BTN,
        )
        self._div(inner, P)

        # ── AI ALGORITHM ──────────────────────────────────────────────────────
        _section_label(inner, "AI ALGORITHM", C["sec_yellow"], P,
                       self.F_SEC).pack(fill="x", pady=(0, 7))
        ar = tk.Frame(inner, bg=P)
        ar.pack()
        self.ai_group = OptionGroup(
            ar,
            [("MINIMAX", "minimax"),
             ("ALPHA-BETA", "alpha_beta")],
            button_w=160, button_h=48,
            sel_color="yellow",
            sound_manager=self.sound_manager,
            on_change=self._on_ai_change,
            icons={"minimax": "▣", "alpha_beta": "◈"},
            btn_font=self.F_BTN,
        )
        self._div(inner, P)

        # ── DIFFICULTY ────────────────────────────────────────────────────────
        self._diff_frame = tk.Frame(inner, bg=P)
        self._diff_frame.pack(fill="x")

        _section_label(self._diff_frame, "DIFFICULTY", C["sec_red"], P,
                       self.F_SEC).pack(fill="x", pady=(0, 7))
        lr = tk.Frame(self._diff_frame, bg=P)
        lr.pack()
        self.level_group = OptionGroup(
            lr,
            [("EASY", "easy"), ("MEDIUM", "medium"), ("HARD", "hard")],
            button_w=160, button_h=48,
            sel_color="red",
            sound_manager=self.sound_manager,
            on_change=self._on_any_change,
            icons={"easy": "○", "medium": "◑", "hard": "●"},
            btn_font=self.F_BTN,
        )
        self._diff_div = tk.Frame(self._diff_frame, bg=C["divider"], height=1)
        self._diff_div.pack(fill="x", pady=11)

        # ── HEURISTIC ─────────────────────────────────────────────────────────
        self._heur_frame = tk.Frame(inner, bg=P)
        self._heur_frame.pack(fill="x")

        _section_label(self._heur_frame, "HEURISTIC", C["sec_yellow"], P,
                       self.F_SEC).pack(fill="x", pady=(0, 7))
        hr = tk.Frame(self._heur_frame, bg=P)
        hr.pack()
        self.heur_group = OptionGroup(
            hr,
            [("H1  BALANCED", "h1"), ("H2  AGGRESSIVE", "h2")],
            button_w=205, button_h=48,
            sel_color="yellow",
            sound_manager=self.sound_manager,
            on_change=self._on_any_change,
            icons={"h1": "◈", "h2": "◆"},
            btn_font=self.F_BTN,
        )
        self._heur_div = tk.Frame(self._heur_frame, bg=C["divider"], height=1)
        self._heur_div.pack(fill="x", pady=11)

        # ── START BUTTON ──────────────────────────────────────────────────────
        self._start_btn = StartButton(inner,
                                      command=self._start,
                                      sound_manager=self.sound_manager,
                                      btn_font=self.F_START)
        self._start_btn.pack(pady=(2, 4))

        self._hint_var = tk.StringVar(
            value="choose: board type, AI algorithm, difficulty, heuristic")
        self._hint_lbl = tk.Label(inner,
                                  textvariable=self._hint_var,
                                  font=self.F_HINT,
                                  fg=C["hint_idle"], bg=P)
        self._hint_lbl.pack()

    # ── helpers ───────────────────────────────────────────────────────────────
    def _div(self, parent, bg):
        tk.Frame(parent, height=1, bg=C["divider"]).pack(fill="x", pady=11)

    def _on_any_change(self, _=None):
        self._refresh_start()

    def _on_ai_change(self, val):
        self._refresh_start()

    def _refresh_start(self):
        ai        = self.ai_group.get()
        diff_ok = self.level_group.is_set()
        ready     = (self.board_group.is_set()
                     and bool(ai)
                     and diff_ok
                     and self.heur_group.is_set())

        if ready:
            self._start_btn.unlock()
            self._hint_var.set("ready — press START to play")
            self._hint_lbl.config(fg=C["hint_ready"])
        else:
            self._start_btn.lock()
            missing = []
            if not self.board_group.is_set():
                missing.append("board type")
            if not ai:
                missing.append("AI algorithm")
            if not self.level_group.is_set():
                missing.append("difficulty")
            if not self.heur_group.is_set():
                missing.append("heuristic")
            self._hint_var.set("choose: " + ",  ".join(missing))
            self._hint_lbl.config(fg=C["hint_idle"])

    # ── title animation ───────────────────────────────────────────────────────
    def _animate_title(self):
        self._pulse = (self._pulse + 0.04) % (2 * math.pi)
        try:
            yg = min(255, int(205 + 50 * math.sin(self._pulse)))
            self.lbl_four.config(fg=f"#f5{yg:02x}00")
            c = max(180, int(200 + 55 * math.sin(self._pulse * 0.7)))
            self.lbl_connect.config(fg=f"#{c:02x}{c:02x}ff")
        except Exception:
            pass
        self._after_ids.append(self.root.after(38, self._animate_title))

    # ── start ─────────────────────────────────────────────────────────────────
    def _start(self):
        depth_map = {"easy": 2, "medium": 4, "hard": 6}
        ai        = self.ai_group.get()
        settings  = {
            "board"     : self.board_group.get(),
            "ai"        : ai,
            "depth": depth_map.get(self.level_group.get(), 4),
            "heuristic" : self.heur_group.get(),
        }
        self.destroy()
        self.on_start(settings)

    def destroy(self):
        for aid in self._after_ids:
            try:
                self.root.after_cancel(aid)
            except Exception:
                pass
        self.frame.destroy()