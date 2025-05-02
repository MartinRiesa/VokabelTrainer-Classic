#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vokabel-Lernspiel (Tkinter) – Progressbar oben & modernes Layout
"""

import random
import tkinter as tk
from tkinter import ttk, messagebox

# --------------------------------------------------------------------------- #
# Daten                                                                      #
# --------------------------------------------------------------------------- #
VOCAB = [
    ("Apfel", "apple"), ("Haus", "house"), ("Hund", "dog"),
    ("Katze", "cat"), ("Stuhl", "chair"), ("Buch", "book"),
    ("Baum", "tree"), ("Wasser", "water"), ("Tisch", "table"),
    ("Auto", "car"), ("Stadt", "city"), ("Freund", "friend"),
    ("Schule", "school"), ("Brot", "bread"), ("Ball", "ball"),
    ("Sonne", "sun"), ("Mond", "moon"), ("Fisch", "fish"),
    ("Milch", "milk"), ("Straße", "street"), ("Zeit", "time"),
]
LEVEL_SIZES = (7, 14, 21)
MAX_STREAK  = 10

# --------------------------------------------------------------------------- #
# Spiel-Klasse                                                               #
# --------------------------------------------------------------------------- #
class VokabelSpiel:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("Vokabel-Lernspiel")
        master.configure(bg="#f0f4f7")

        # ---------- Style -------------------------------------------------- #
        style = ttk.Style(master)
        style.theme_use("clam")
        style.configure("TButton",
                        font=("Arial", 13),
                        padding=6,
                        relief="flat")
        style.map("TButton",
                  foreground=[("active", "#ffffff")],
                  background=[("active", "#4676f2")])
        style.configure("bar.Horizontal.TProgressbar", thickness=18)

        # ---------- Layout: Frames ----------------------------------------- #
        top_frame    = tk.Frame(master, bg="#f0f4f7")
        center_frame = tk.Frame(master, bg="#f0f4f7")
        bottom_frame = tk.Frame(master, bg="#f0f4f7")

        top_frame.pack(fill="x", pady=(15, 0))
        center_frame.pack(fill="both", expand=True)
        bottom_frame.pack(fill="x", pady=(0, 15))

        # ---------- Progressbar & Status oben ------------------------------ #
        self.progress = ttk.Progressbar(top_frame,
                                        length=380,
                                        mode="determinate",
                                        maximum=MAX_STREAK,
                                        style="bar.Horizontal.TProgressbar")
        self.progress.pack(pady=4)

        self.status_var = tk.StringVar()
        ttk.Label(top_frame,
                  textvariable=self.status_var,
                  font=("Arial", 11),
                  background="#f0f4f7").pack()

        # ---------- Frage --------------------------------------------------- #
        self.question_var = tk.StringVar()
        ttk.Label(center_frame,
                  textvariable=self.question_var,
                  font=("Arial", 17, "bold"),
                  wraplength=380,
                  justify="center",
                  background="#f0f4f7").pack(pady=(30, 20))

        # ---------- Antwort-Buttons ---------------------------------------- #
        self.option_buttons: list[ttk.Button] = []
        for _ in range(4):
            btn = ttk.Button(center_frame)
            btn.pack(fill="x", pady=6, padx=60)
            self.option_buttons.append(btn)

        # ---------- Spiel-Status ------------------------------------------- #
        self.level  = 0
        self.streak = 0
        self.level_vocab: list[tuple[str, str]] = []
        self.start_level()

    # --------------------------------------------------------------------- #
    def start_level(self) -> None:
        self.level += 1
        if self.level > 3:
            messagebox.showinfo("Geschafft",
                                "🎉 Herzlichen Glückwunsch – alle Level abgeschlossen! 🎉")
            self.master.quit()
            return

        self.level_vocab = VOCAB[:LEVEL_SIZES[self.level - 1]]
        self.streak = 0
        self.update_progress()
        self.status_var.set(f"Level {self.level} – 0/{MAX_STREAK} richtige Folge")
        self.next_question()

    # --------------------------------------------------------------------- #
    def next_question(self) -> None:
        de, self.correct_en = random.choice(self.level_vocab)
        self.question_var.set(f"Was heißt „{de}“ auf Englisch?")

        wrong = [en for _, en in self.level_vocab if en != self.correct_en]
        options = random.sample(wrong, 3) + [self.correct_en]
        random.shuffle(options)

        for btn, ans in zip(self.option_buttons, options):
            btn.config(text=ans,
                       command=lambda a=ans: self.check_answer(a))

    # --------------------------------------------------------------------- #
    def check_answer(self, selected: str) -> None:
        if selected == self.correct_en:
            self.streak += 1
            self.update_progress()
            self.status_var.set(
                f"Level {self.level} – {self.streak}/{MAX_STREAK} richtige Folge")
            if self.streak == MAX_STREAK:
                messagebox.showinfo("Level geschafft",
                                    f"Level {self.level} abgeschlossen!")
                self.start_level()
            else:
                self.next_question()
        else:
            messagebox.showwarning("Falsch",
                                   "Leider falsch! Der Zähler wird zurückgesetzt.")
            self.streak = 0
            self.update_progress()
            self.status_var.set(f"Level {self.level} – 0/{MAX_STREAK} richtige Folge")
            self.next_question()

    # --------------------------------------------------------------------- #
    def update_progress(self) -> None:
        self.progress["value"] = self.streak

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("450x500")
    root.resizable(False, False)
    VokabelSpiel(root)
    root.mainloop()
