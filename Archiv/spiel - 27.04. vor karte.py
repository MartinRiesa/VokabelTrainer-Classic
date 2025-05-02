#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vokabellernspiel – pro Level eigenes Poster + Vorhang
"""

import os, random, datetime as dt, tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

CURTAIN_FILE   = "Vorhang.png"
POSTER_PATTERN = "{}.jpg"          # 1.jpg, 2.jpg, …
BANNER_W, BANNER_H = 960, 360
STREAK_GOAL       = 10
SPACING_MIN       = (1, 10, 60, 720, 1440, 4320)

VOCAB = [  # 21 Wörter, kumulativ genutzt
    ("Apfel","apple"), ("Haus","house"), ("Hund","dog"), ("Katze","cat"),
    ("Stuhl","chair"), ("Buch","book"), ("Baum","tree"), ("Wasser","water"),
    ("Tisch","table"), ("Auto","car"), ("Stadt","city"), ("Freund","friend"),
    ("Schule","school"), ("Brot","bread"), ("Ball","ball"), ("Sonne","sun"),
    ("Mond","moon"), ("Fisch","fish"), ("Milch","milk"), ("Straße","street"),
    ("Zeit","time")
]

class Stat:
    def __init__(self):
        self.EF, self.n, self.i = 2.5, 0, 1
        self.due = dt.datetime.now()

class Spiel:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Vokabellernspiel")
        root.geometry("1000x860")
        root.configure(bg="#eef4fb")

        # ─ Banner --------------------------------------------------------
        banner = tk.Frame(root, bg="#eef4fb"); banner.pack(pady=10)
        self.canvas = tk.Canvas(banner, width=BANNER_W, height=BANNER_H,
                                highlightthickness=0)
        self.canvas.pack()

        # Erst das Poster-Objekt (Platzhalter), danach der Vorhang
        self.poster = self.canvas.create_image(0, 0, anchor="nw")
        self.curtain_full = Image.open(CURTAIN_FILE).convert("RGBA") \
                              .resize((BANNER_W, BANNER_H), Image.LANCZOS)
        self.curtain_img = ImageTk.PhotoImage(self.curtain_full)
        self.curtain = self.canvas.create_image(0, 0, anchor="nw",
                                                image=self.curtain_img)
        self.curtain_offset = 0

        # ─ Infozeile -----------------------------------------------------
        info = tk.Frame(root, bg="#eef4fb"); info.pack(pady=5)
        self.level_var = tk.StringVar(value="Level 1")
        ttk.Label(info, textvariable=self.level_var,
                  font=("Arial", 14, "bold")).pack(side="left", padx=12)
        self.opt_free = tk.BooleanVar(); self.opt_rev = tk.BooleanVar()
        ttk.Checkbutton(info, text="Freitexteingabe",
                        variable=self.opt_free).pack(side="left")
        ttk.Checkbutton(info, text="Reverse (EN→DE)",
                        variable=self.opt_rev).pack(side="left")

        # ─ Spielfläche ---------------------------------------------------
        play = tk.Frame(root, bg="#eef4fb"); play.pack(expand=True, fill="both")
        self.qvar = tk.StringVar()
        ttk.Label(play, textvariable=self.qvar,
                  font=("Arial", 28, "bold"), background="#eef4fb"
                 ).pack(pady=(30, 15))
        self.btns = [tk.Button(play, font=("Arial", 16), width=26)
                     for _ in range(4)]
        for b in self.btns: b.pack(pady=8)
        self.next_btn = ttk.Button(play, text="Weiter",
                                   command=lambda: self.next_question())

        # ─ Lernstatus ----------------------------------------------------
        self.stats  = {d: Stat() for d,_ in VOCAB}
        self.streak = 0
        self.level  = 1
        self.level_vocab = VOCAB[:7]

        self.set_poster(self.level)     # Poster 1.jpg laden
        self.next_question()

    # ---------- Poster laden / Ebenenreihenfolge sichern ----------------
    def set_poster(self, lvl: int):
        fname = POSTER_PATTERN.format(lvl)
        while not os.path.exists(fname) and lvl > 1:
            lvl -= 1; fname = POSTER_PATTERN.format(lvl)

        if not os.path.exists(fname):
            messagebox.showerror("Poster fehlt",
                                 f"Keine Posterdatei '{fname}' gefunden.")
            self.root.quit(); return

        img = Image.open(fname).resize((BANNER_W, BANNER_H), Image.LANCZOS)
        self.poster_img = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.poster, image=self.poster_img)
        # Poster nach unten, Vorhang nach oben
        self.canvas.tag_lower(self.poster, self.curtain)

    # ---------- Vorhang -------------------------------------------------
    def update_curtain(self):
        crop = self.curtain_full.crop(
            (0, self.curtain_offset, BANNER_W, BANNER_H))
        self.curtain_img = ImageTk.PhotoImage(crop)
        self.canvas.itemconfig(self.curtain, image=self.curtain_img)

    def pull_curtain(self):
        step = BANNER_H // STREAK_GOAL
        self.curtain_offset = min(self.curtain_offset + step, BANNER_H)
        self.update_curtain()

    def reset_curtain(self):
        self.curtain_offset = 0
        self.update_curtain()

    # ---------- Spielmechanik ------------------------------------------
    def next_question(self):
        self.next_btn.pack_forget()
        for b in self.btns: b.config(state="normal", bg="SystemButtonFace")

        due = [(d,e) for d,e in self.level_vocab
               if self.stats[d].due <= dt.datetime.now()] or self.level_vocab
        self.de, self.en = random.choice(due)

        opts = [self.en] + random.sample(
            [x for _, x in self.level_vocab if x != self.en], 3)
        random.shuffle(opts)
        self.qvar.set(self.de)

        for btn, txt in zip(self.btns, opts):
            btn.config(text=txt,
                       command=lambda t=txt, b=btn: self.evaluate(t, b))

    def evaluate(self, ans: str, btn: tk.Button):
        correct = ans == self.en
        s = self.stats[self.de]

        if correct:
            self.streak += 1
            self.pull_curtain()
            s.i = 1 if s.n == 0 else (2 if s.n == 1 else
                  min(s.i + 1, len(SPACING_MIN) - 1))
            s.n += 1
            s.due = dt.datetime.now() + dt.timedelta(
                minutes=SPACING_MIN[s.i])

            if self.streak == STREAK_GOAL:
                self.level_up()
            else:
                self.next_question()
        else:
            for b in self.btns:
                if b["text"] == self.en:
                    b.config(bg="#58d068")
                elif b is btn:
                    b.config(bg="#e05757")
                b.config(state="disabled")

            self.streak = 0
            self.reset_curtain()
            s.n = s.i = 0
            s.due = dt.datetime.now() + dt.timedelta(
                minutes=SPACING_MIN[0])
            self.next_btn.pack(pady=20)

    # ---------- Levelwechsel -------------------------------------------
    def level_up(self):
        if self.level >= 3:
            messagebox.showinfo("Fertig", "Alle Level bestanden!")
            self.root.quit(); return

        self.level += 1
        self.level_var.set(f"Level {self.level}")
        self.level_vocab = VOCAB[:7 * self.level]
        self.set_poster(self.level)
        self.reset_curtain()
        self.streak = 0
        messagebox.showinfo("Level geschafft",
                            f"Starte Level {self.level}")
        self.next_question()

# ---------- Start ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    Spiel(root)
    root.mainloop()
