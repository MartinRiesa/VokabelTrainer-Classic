#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vokabel-Lernspiel – Banner (960×360) mit Vorhang
"""

import os, random, datetime as dt, tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk      # pip install pillow

POSTER_FILE, CURTAIN_FILE = "Erinnerungen.jpg", "Vorhang.png"
BANNER_W, BANNER_H = 960, 360
STREAK_GOAL = 10
SPACING_MIN = (1, 10, 60, 720, 1440, 4320)

VOCAB = [
    ("Apfel", "apple"), ("Haus", "house"), ("Hund", "dog"), ("Katze", "cat"),
    ("Stuhl", "chair"), ("Buch", "book"), ("Baum", "tree"), ("Wasser", "water"),
    ("Tisch", "table"), ("Auto", "car"), ("Stadt", "city"), ("Freund", "friend"),
    ("Schule", "school"), ("Brot", "bread"), ("Ball", "ball"), ("Sonne", "sun"),
    ("Mond", "moon"), ("Fisch", "fish"), ("Milch", "milk"), ("Straße", "street"),
    ("Zeit", "time")
]

class Stat:
    def __init__(self):
        self.EF, self.n, self.i = 2.5, 0, 1
        self.due = dt.datetime.now()
        self.wrong = []

class Spiel:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Vokabellernspiel")
        root.geometry("1000x860")
        root.configure(bg="#eef4fb")

        # ─ Banner
        banner_fr = tk.Frame(root, bg="#eef4fb", height=BANNER_H)
        banner_fr.pack(pady=10)

        self.canvas = tk.Canvas(banner_fr,
                                width=BANNER_W,
                                height=BANNER_H,
                                highlightthickness=0)
        self.canvas.pack()

        self.poster_img, self.curtain_full = self.load_images()
        self.canvas.create_image(0, 0, anchor="nw", image=self.poster_img)
        self.curtain_img = ImageTk.PhotoImage(self.curtain_full)
        self.curtain = self.canvas.create_image(0, 0, anchor="nw",
                                                image=self.curtain_img)
        self.curtain_offset = 0

        # ─ Infozeile (Level & Optionen)
        info = tk.Frame(root, bg="#eef4fb")
        info.pack(pady=5)

        self.level_var = tk.StringVar(value="Level 1")
        ttk.Label(info,
                  textvariable=self.level_var,
                  font=("Arial", 14, "bold")).pack(side="left", padx=12)

        self.opt_free = tk.BooleanVar()
        self.opt_rev = tk.BooleanVar()

        cb_free = ttk.Checkbutton(info,
                                  text="Freitexteingabe",
                                  variable=self.opt_free)
        cb_free.pack(side="left")

        cb_rev = ttk.Checkbutton(info,
                                 text="Reverse (EN→DE)",
                                 variable=self.opt_rev)
        cb_rev.pack(side="left")

        # ─ Spielfläche
        play = tk.Frame(root, bg="#eef4fb")
        play.pack(expand=True, fill="both")

        self.qvar = tk.StringVar()
        ttk.Label(play,
                  textvariable=self.qvar,
                  font=("Arial", 28, "bold"),
                  background="#eef4fb").pack(pady=(30, 15))

        self.btns = [tk.Button(play, font=("Arial", 16), width=26)
                     for _ in range(4)]
        for b in self.btns:
            b.pack(pady=8)

        self.next_btn = ttk.Button(play, text="Weiter",
                                   command=self.after_wrong)

        # ─ Lernstatus
        self.stats = {d: Stat() for d, _ in VOCAB}
        self.streak = 0
        self.level = 1
        self.level_vocab = VOCAB[:7]

        self.next_question()

    # ─ Hilfsfunktionen Bilder
    def load_images(self):
        if not (os.path.exists(POSTER_FILE) and os.path.exists(CURTAIN_FILE)):
            messagebox.showerror("Fehler",
                                 "Poster oder Vorhang fehlen im Verzeichnis.")
            self.root.quit()

        poster = Image.open(POSTER_FILE).resize((BANNER_W, BANNER_H),
                                                Image.LANCZOS)
        curtain = Image.open(CURTAIN_FILE).convert("RGBA") \
                   .resize((BANNER_W, BANNER_H), Image.LANCZOS)
        return ImageTk.PhotoImage(poster), curtain

    # ─ Vorhangsteuerung
    def update_curtain(self):
        crop = self.curtain_full.crop(
            (0, self.curtain_offset, BANNER_W, BANNER_H))
        self.curtain_img = ImageTk.PhotoImage(crop)
        self.canvas.itemconfig(self.curtain, image=self.curtain_img)

    def pull_curtain(self):
        self.curtain_offset = min(self.curtain_offset +
                                  BANNER_H // STREAK_GOAL, BANNER_H)
        self.update_curtain()

    def reset_curtain(self):
        self.curtain_offset = 0
        self.update_curtain()

    # ─ Spielablauf
    def next_question(self):
        for b in self.btns:
            b.config(state="normal", bg="SystemButtonFace")
        self.next_btn.pack_forget()

        due = [(d, e) for d, e in self.level_vocab
               if self.stats[d].due <= dt.datetime.now()] or self.level_vocab
        d, e = random.choice(due)
        self.de, self.en = d, e

        wrong = [x for _, x in self.level_vocab if x != e]
        opts = [e] + random.sample(wrong, 3)
        random.shuffle(opts)

        self.qvar.set(d)
        for btn, txt in zip(self.btns, opts):
            btn.config(text=txt,
                       command=lambda t=txt, b=btn: self.evaluate(t, b))

    def evaluate(self, ans: str, btn: tk.Button):
        correct = ans == self.en
        stat = self.stats[self.de]

        if correct:
            self.streak += 1
            self.pull_curtain()
            stat.i = 1 if stat.n == 0 else \
                     (2 if stat.n == 1 else
                      min(stat.i + 1, len(SPACING_MIN) - 1))
            stat.n += 1
            stat.due = dt.datetime.now() + dt.timedelta(
                minutes=SPACING_MIN[stat.i])

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
            stat.n = stat.i = 0
            stat.due = dt.datetime.now() + dt.timedelta(
                minutes=SPACING_MIN[0])
            self.next_btn.pack(pady=20)

    def after_wrong(self):
        self.next_question()

    def level_up(self):
        messagebox.showinfo("Level geschafft",
                            "Vorhang vollständig geöffnet!")
        if self.level < 3:
            self.level += 1
            self.level_var.set(f"Level {self.level}")
            self.level_vocab = VOCAB[:7 * self.level]
            self.streak = 0
            self.reset_curtain()
            self.next_question()
        else:
            messagebox.showinfo("Fertig", "Alle Level bestanden!")
            self.root.quit()

# ─ Start
if __name__ == "__main__":
    root = tk.Tk()
    Spiel(root)
    root.mainloop()
