#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vokabel-Lernspiel mit Mausklick-Interface (Tkinter)

• Level 1:  7 Vokabeln
• Level 2: 14 Vokabeln (Level 1 + 7 neue)
• Level 3: 21 Vokabeln (alle)

Ziel pro Level: 10 richtige Antworten in Folge.
Bei Fehler ⇒ Zähler 0, Level beginnt neu.
"""

import random
import tkinter as tk
from tkinter import messagebox

# --- Feste Vokabelliste ------------------------------------------------------
VOCAB = [
    ("Apfel", "apple"),     ("Haus", "house"),     ("Hund", "dog"),
    ("Katze", "cat"),       ("Stuhl", "chair"),    ("Buch", "book"),
    ("Baum", "tree"),       ("Wasser", "water"),   ("Tisch", "table"),
    ("Auto", "car"),        ("Stadt", "city"),     ("Freund", "friend"),
    ("Schule", "school"),   ("Brot", "bread"),     ("Ball", "ball"),
    ("Sonne", "sun"),       ("Mond", "moon"),      ("Fisch", "fish"),
    ("Milch", "milk"),      ("Straße", "street"),  ("Zeit", "time"),
]

LEVEL_SIZES = (7, 14, 21)  # Wörter je Level


# --- Spielklasse -------------------------------------------------------------
class VokabelSpiel:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("Vokabel-Lernspiel")

        # UI-Elemente ---------------------------------------------------------
        self.question_var = tk.StringVar()
        tk.Label(master,
                 textvariable=self.question_var,
                 font=("Arial", 16),
                 wraplength=380,
                 justify="center").pack(pady=12)

        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=6)

        self.option_buttons: list[tk.Button] = []
        for _ in range(4):
            btn = tk.Button(btn_frame,
                            width=22,
                            font=("Arial", 13),
                            relief="raised")
            btn.pack(pady=4, fill="x")
            self.option_buttons.append(btn)

        self.status_var = tk.StringVar()
        tk.Label(master,
                 textvariable=self.status_var,
                 font=("Arial", 12)).pack(pady=10)

        # Spielstatus ---------------------------------------------------------
        self.level = 0           # wird in start_level erhöht
        self.streak = 0
        self.level_vocab: list[tuple[str, str]] = []

        self.start_level()       # Level 1 laden

    # ----------------------- Spielsteuerung ----------------------------------
    def start_level(self) -> None:
        """Neues Level initialisieren oder Spiel beenden."""
        self.level += 1
        if self.level > 3:
            messagebox.showinfo("Geschafft",
                                "🎉 Herzlichen Glückwunsch – alle Level abgeschlossen! 🎉")
            self.master.quit()
            return

        self.level_vocab = VOCAB[:LEVEL_SIZES[self.level - 1]]
        self.streak = 0
        self.status_var.set(f"Level {self.level} – 0/10 richtige Folge")
        self.next_question()

    def next_question(self) -> None:
        """Neue Frage anzeigen und Buttons konfigurieren."""
        de, self.correct_en = random.choice(self.level_vocab)
        self.question_var.set(f"Was heißt „{de}“ auf Englisch?")

        # Drei falsche + korrekte Antwort mischen
        wrong = [en for _, en in self.level_vocab if en != self.correct_en]
        options = random.sample(wrong, 3) + [self.correct_en]
        random.shuffle(options)

        for btn, ans in zip(self.option_buttons, options):
            btn.config(text=ans,
                       command=lambda a=ans: self.check_answer(a))

    # ----------------------- Antwortbewertung --------------------------------
    def check_answer(self, selected: str) -> None:
        if selected == self.correct_en:
            self.streak += 1
            self.status_var.set(
                f"Level {self.level} – {self.streak}/10 richtige Folge")
            if self.streak == 10:
                messagebox.showinfo("Level geschafft",
                                    f"Level {self.level} abgeschlossen!")
                self.start_level()
            else:
                self.next_question()
        else:
            messagebox.showwarning("Falsch",
                                   "Leider falsch! Der Zähler wird zurückgesetzt.")
            self.streak = 0
            self.status_var.set(f"Level {self.level} – 0/10 richtige Folge")
            self.next_question()


# --- Hauptteil ---------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("420x370")   # kompakte Fenstergröße
    root.resizable(False, False)
    game = VokabelSpiel(root)
    root.mainloop()
