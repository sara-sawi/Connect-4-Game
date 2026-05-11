import tkinter as tk
from PIL import Image, ImageTk
import math
import os
import random


class SplashScreen:
    def __init__(self, root, on_complete, sound_manager=None):
        self.root = root
        self.on_complete = on_complete
        self.sound_manager = sound_manager
        self._after_ids = []
        self.progress = 0
        self.glow_pulse = 0
        self.particles = []

        self.frame = tk.Frame(root, bg="#0a0a1a")
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.canvas = tk.Canvas(self.frame, bg="#0a0a1a", highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.root.update()
        self.W = self.root.winfo_width()
        self.H = self.root.winfo_height()

        self._start_btn = None   # created after load completes
        self._load_complete = False

        self._draw_background()
        self._build_title()
        self._build_loader()
        self._spawn_particles()
        self._animate()
        self._load_progress()

        # Redraw all static elements when the window is resized
        self.canvas.bind("<Configure>", self._on_resize)

    # ── background ────────────────────────────────────────────────────────────
    def _draw_background(self):
        W, H = self.W, self.H
        base = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base, "background.jpg")

        if os.path.exists(bg_path):
            try:
                img = Image.open(bg_path).resize((W, H), Image.LANCZOS)
                # darken the image so text stays readable
                overlay = Image.new("RGBA", (W, H), (0, 0, 20, 180))
                img = img.convert("RGBA")
                img = Image.alpha_composite(img, overlay).convert("RGB")
                self._bg_photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self._bg_photo, anchor="nw")
            except Exception as e:
                print(f"[WARN] Could not load background.jpg: {e}")
                self._draw_fallback_bg()
        else:
            print("[INFO] background.jpg not found — using fallback gradient.")
            self._draw_fallback_bg()

        # grid lines on top
        step = 60
        for x in range(0, W, step):
            self.canvas.create_line(x, 0, x, H, fill="#1a1a3a", width=1)
        for y in range(0, H, step):
            self.canvas.create_line(0, y, W, y, fill="#1a1a3a", width=1)

        # corner glows
        for cx, cy, r, col in [
            (-40, -40,  120, "#1e0060"),
            (W+40, -40,  120, "#003060"),
            (-40,  H+40, 120, "#002060"),
            (W+40, H+40, 120, "#1e0040"),
        ]:
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                    fill=col, outline="")

    def _draw_fallback_bg(self):
        W, H = self.W, self.H
        for i in range(30):
            shade = int(10 + i * 1.8)
            col = f"#{shade:02x}{shade:02x}{min(255, shade+18):02x}"
            self.canvas.create_rectangle(
                0, H*i//30, W, H*(i+1)//30, fill=col, outline="")

    # ── title ─────────────────────────────────────────────────────────────────
    def _build_title(self):
        W, H = self.W, self.H
        cx, cy = W//2, H//2

        # shadow layers
        for off, col in [(10, "#0d0040"), (6, "#1a0070"), (3, "#2800a0")]:
            self.canvas.create_text(cx+off, cy-85+off, text="",
                                    font=("Impact", 72, "bold"), fill=col, anchor="center")
            self.canvas.create_text(cx+off, cy+5+off,  text="CONNECT 4",
                                    font=("Impact", 72, "bold"), fill=col, anchor="center")

        # main text
        self.title_connect = self.canvas.create_text(
            cx, cy-85, text="",
            font=("Impact", 72, "bold"), fill="#ffffff", anchor="center")

        self.title_four = self.canvas.create_text(
            cx, cy+5, text="CONNECT 4",
            font=("Impact", 72, "bold"), fill="#f7df00", anchor="center")

        self.canvas.create_text(cx, cy+80,
            text="✦   A I   E D I T I O N   ✦",
            font=("Courier", 15, "bold"), fill="#7878ff", anchor="center")

        self.canvas.create_line(cx-170, cy+102, cx+170, cy+102,
                                fill="#3333aa", width=1)

    # ── loading bar ───────────────────────────────────────────────────────────
    def _build_loader(self):
        W, H = self.W, self.H
        cx = W//2
        cy = H - 90
        bw, bh = 340, 18

        self.canvas.create_text(cx, cy-26, text="LOADING…",
                                font=("Courier", 11), fill="#5555aa", anchor="center")

        self.canvas.create_rectangle(cx-bw//2, cy-bh//2,
                                      cx+bw//2, cy+bh//2,
                                      fill="#1a1a3a", outline="#3a3aaa", width=1)

        self.bar_fill = self.canvas.create_rectangle(
            cx-bw//2+2, cy-bh//2+2,
            cx-bw//2+2, cy+bh//2-2,
            fill="#4444ff", outline="")

        self.pct_text = self.canvas.create_text(
            cx, cy+20, text="0%",
            font=("Courier", 10), fill="#5555aa", anchor="center")

        self._bar_cx = cx
        self._bar_bw = bw
        self._bar_bh = bh
        self._bar_cy = cy

    # ── particles ─────────────────────────────────────────────────────────────
    def _spawn_particles(self):
        W, H = self.W, self.H
        for _ in range(35):
            x  = random.randint(0, W)
            y  = random.randint(0, H)
            r  = random.uniform(1.5, 4)
            dy = random.uniform(-0.3, -1.1)
            dx = random.uniform(-0.3, 0.3)
            col = random.choice(["#3333bb", "#e63950", "#f7df00", "#5555ff"])
            item = self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                           fill=col, outline="")
            self.particles.append({"item": item, "x": x, "y": y,
                                   "dx": dx, "dy": dy, "r": r})

    # ── animation ─────────────────────────────────────────────────────────────
    def _animate(self):
        W, H = self.W, self.H
        self.glow_pulse = (self.glow_pulse + 0.055) % (2*math.pi)

        g = int(85 + 60 * math.sin(self.glow_pulse))
        self.canvas.itemconfig(self.title_connect, fill=f"#{g:02x}{g:02x}ff")

        yg = min(255, int(215 + 40 * math.sin(self.glow_pulse + 1)))
        self.canvas.itemconfig(self.title_four, fill=f"#f7{yg:02x}00")

        for p in self.particles:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            if p["y"] < -10:
                p["y"] = H + 10
                p["x"] = random.randint(0, W)
            r = p["r"]
            self.canvas.coords(p["item"], p["x"]-r, p["y"]-r,
                               p["x"]+r, p["y"]+r)

        self._after_ids.append(self.root.after(30, self._animate))

    # ── progress bar ──────────────────────────────────────────────────────────
    def _load_progress(self):
        if self.progress >= 100:
            self.canvas.itemconfig(self.pct_text, text="100%  ✓")
            self._load_complete = True
            self._after_ids.append(self.root.after(400, self._show_start_button))
            return

        self.progress += 1 if self.progress < 90 else 0.4
        pct = min(self.progress, 100)
        fill_w = int((pct / 100) * (self._bar_bw - 4))

        if pct < 50:
            r, g, b = 68, 68, 255
        elif pct < 80:
            r, g, b = 255, int(68 + (pct-50)*5.5), 68
        else:
            r, g, b = 68, 200, 68

        cx, bw, bh, cy = self._bar_cx, self._bar_bw, self._bar_bh, self._bar_cy
        self.canvas.coords(self.bar_fill,
                           cx-bw//2+2, cy-bh//2+2,
                           cx-bw//2+2+fill_w, cy+bh//2-2)
        self.canvas.itemconfig(self.bar_fill, fill=f"#{r:02x}{g:02x}{b:02x}")
        self.canvas.itemconfig(self.pct_text, text=f"{int(pct)}%")

        delay = 35 if self.progress < 90 else 70
        self._after_ids.append(self.root.after(delay, self._load_progress))

    # ── start button ──────────────────────────────────────────────────────────
    def _show_start_button(self):
        cx = self.W // 2
        cy = self.H - 90
        btn_w, btn_h = 220, 52
        x1 = cx - btn_w // 2
        y1 = cy + 36
        x2 = cx + btn_w // 2
        y2 = y1 + btn_h

        # glow halo
        self.canvas.create_oval(x1-10, y1-10, x2+10, y2+10,
                                fill="#0a0a4a", outline="#3333bb", width=2,
                                tags="startbtn")
        # button background
        self._start_bg = self.canvas.create_rectangle(
            x1, y1, x2, y2, fill="#0d0033", outline="#6644ff", width=3,
            tags="startbtn")
        # button text
        self._start_txt = self.canvas.create_text(
            cx, y1 + btn_h // 2,
            text="▶   ENTER GAME",
            font=("Impact", 18), fill="#e0d4ff",
            tags="startbtn")

        # hover effect
        def on_enter(_):
            self.canvas.itemconfig(self._start_bg, fill="#1a0066")
            self.canvas.itemconfig(self._start_txt, fill="#ffffff")
        def on_leave(_):
            self.canvas.itemconfig(self._start_bg, fill="#0d0033")
            self.canvas.itemconfig(self._start_txt, fill="#e0d4ff")
        def on_click(_):
            if self.sound_manager:
                self.sound_manager.play_click()
            self._destroy()

        self.canvas.tag_bind("startbtn", "<Enter>",    on_enter)
        self.canvas.tag_bind("startbtn", "<Leave>",    on_leave)
        self.canvas.tag_bind("startbtn", "<Button-1>", on_click)

        # animate the button pulsing
        self._pulse_start_btn()

    def _pulse_start_btn(self):
        import math
        t = (getattr(self, "_btn_pulse_t", 0) + 0.08) % (2 * math.pi)
        self._btn_pulse_t = t
        alpha = int(180 + 75 * math.sin(t))
        col = f"#{alpha:02x}{int(alpha*0.85):02x}ff"
        self.canvas.itemconfig(self._start_bg, outline=col)
        self._after_ids.append(self.root.after(40, self._pulse_start_btn))

    # ── resize handler ────────────────────────────────────────────────────────
    def _on_resize(self, event):
        new_w = event.width
        new_h = event.height
        if new_w == self.W and new_h == self.H:
            return
        self.W = new_w
        self.H = new_h
        # Redraw everything at the new size
        self.canvas.delete("all")
        self.particles.clear()
        self._draw_background()
        self._build_title()
        self._build_loader()
        # Restore progress bar to current progress level
        pct = min(self.progress, 100)
        fill_w = int((pct / 100) * (self._bar_bw - 4))
        cx, bw, bh, cy = self._bar_cx, self._bar_bw, self._bar_bh, self._bar_cy
        self.canvas.coords(self.bar_fill,
                           cx-bw//2+2, cy-bh//2+2,
                           cx-bw//2+2+fill_w, cy+bh//2-2)
        self.canvas.itemconfig(self.pct_text, text=f"{int(pct)}%")
        self._spawn_particles()
        if self._load_complete:
            self._show_start_button()

    # ── teardown ──────────────────────────────────────────────────────────────
    def _destroy(self):
        for aid in self._after_ids:
            try:
                self.root.after_cancel(aid)
            except Exception:
                pass
        self.frame.destroy()
        self.on_complete()