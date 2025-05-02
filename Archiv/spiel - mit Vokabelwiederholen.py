#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vokabel-Lernspiel (Tkinter) mit Weighted Adaptive Spaced Repetition

• Falsch getippte Wörter werden häufiger wiederholt
• Richtig beherrschte Wörter erhalten wachsende Intervalle (SM-2-Logik)
• Lautsprecher-Button (pyttsx3) für die Aussprache
• Fortschrittsbalken, modernes Layout
"""

import random
import tkinter as tk
from tkinter import ttk, messagebox

# --------------------------------------------------------------------------- #
# Daten                                                                       #
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
LEVEL_SIZES = (7, 14, 21)     # Wörter pro Level
MAX_STREAK  = 10              # Richtige in Folge zum Level-Abschluss
BIAS        = 0.5             # Gewichtungs-Bias im Auswahl-Roulette

# --------------------------------------------------------------------------- #
class VokabelSpiel:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("Vokabel-Lernspiel")
        master.configure(bg="#f0f4f7")

        # ---------- TTS-Engine (optional) ---------------------------------- #
        try:
            import pyttsx3  # type: ignore
            self.engine = pyttsx3.init()
        except ImportError:
            self.engine = None

        # ---------- ttk-Style --------------------------------------------- #
        style = ttk.Style(master)
        style.theme_use("clam")
        style.configure("TButton", font=("Arial", 13), padding=6, relief="flat")
        style.map("TButton",
                  foreground=[("active", "#ffffff")],
                  background=[("active", "#4676f2")])
        style.configure("bar.Horizontal.TProgressbar", thickness=18)

        # ---------- Layout-Frames ----------------------------------------- #
        top_frame    = tk.Frame(master, bg="#f0f4f7")
        center_frame = tk.Frame(master, bg="#f0f4f7")
        bottom_frame = tk.Frame(master, bg="#f0f4f7")

        top_frame.pack(fill="x", pady=(15, 0))
        center_frame.pack(fill="both", expand=True)
        bottom_frame.pack(fill="x", pady=(0, 15))

        # ---------- Progressbar & Status ---------------------------------- #
        self.progress = ttk.Progressbar(top_frame,
                                        length=380,
                                        maximum=MAX_STREAK,
                                        mode="determinate",
                                        style="bar.Horizontal.TProgressbar")
        self.progress.pack(pady=4)

        self.status_var = tk.StringVar()
        ttk.Label(top_frame,
                  textvariable=self.status_var,
                  font=("Arial", 11),
                  background="#f0f4f7").pack()

        # ---------- Wort-Anzeige + Lautsprecher --------------------------- #
        question_frame = tk.Frame(center_frame, bg="#f0f4f7")
        question_frame.pack(pady=(40, 20))

        self.question_var = tk.StringVar()
        ttk.Label(question_frame,
                  textvariable=self.question_var,
                  font=("Arial", 22, "bold"),
                  background="#f0f4f7").pack(side="left", padx=(0, 10))

        self.speaker_btn = ttk.Button(question_frame,
                                      text="🔊",
                                      width=3,
                                      command=self.speak_word)
        self.speaker_btn.pack(side="left")

        # ---------- Antwort-Buttons --------------------------------------- #
        self.option_buttons: list[ttk.Button] = []
        for _ in range(4):
            btn = ttk.Button(center_frame)
            btn.pack(fill="x", pady=6, padx=60)
            self.option_buttons.append(btn)

        # ---------- Lernstatistiken --------------------------------------- #
        # Struktur je Wort: {EF, n, I, due}
        self.stats: dict[str, dict[str, float | int]] = {}
        for de, _ in VOCAB:
            self.stats[de] = {"EF": 2.5, "n": 0, "I": 1, "due": 0}

        # ---------- Spiel-Status ------------------------------------------ #
        self.level = 0
        self.streak = 0
        self.level_vocab: list[tuple[str, str]] = []
        self.current_de: str = ""
        self.start_level()

    # --------------------------------------------------------------------- #
    # Level-Steuerung
    def start_level(self) -> None:
        self.level += 1
        if self.level > 3:
            messagebox.showinfo("Geschafft",
                                "🎉 Herzlichen Glückwunsch – alle Level abgeschlossen! 🎉")
            self.master.quit()
            return

        # neue Wörter zum Statistik-Pool hinzufügen
        self.level_vocab = VOCAB[:LEVEL_SIZES[self.level - 1]]
        self.streak = 0
        self.update_progress()
        self.status_var.set(f"Level {self.level} – 0/{MAX_STREAK} richtige Folge")
        self.next_question()

    # --------------------------------------------------------------------- #
    # Auswahl einer neuen Frage (W-ASR)
    def choose_word(self) -> tuple[str, str]:
        # Countdown verringern
        for de, _ in self.level_vocab:
            if self.stats[de]["due"] > 0:
                self.stats[de]["due"] -= 1

        # Kandidaten, die fällig sind (due == 0)
        available = [(de, en) for de, en in self.level_vocab
                     if self.stats[de]["due"] == 0]

        # Fallback, falls alle due > 0
        if not available:
            available = self.level_vocab

        # Gewicht berechnen
        weights = [1.0 / (self.stats[de]["I"] + BIAS) for de, _ in available]
        chosen = random.choices(population=available, weights=weights, k=1)[0]
        return chosen

    # --------------------------------------------------------------------- #
    def next_question(self) -> None:
        self.current_de, self.correct_en = self.choose_word()
        self.question_var.set(self.current_de)          # Nur das Wort anzeigen

        wrong = [en for de, en in self.level_vocab if en != self.correct_en]
        options = random.sample(wrong, 3) + [self.correct_en]
        random.shuffle(options)

        for btn, ans in zip(self.option_buttons, options):
            btn.config(text=ans,
                       command=lambda a=ans: self.check_answer(a))

    # --------------------------------------------------------------------- #
    # Antwortbewertung + Statistik-Update
    def check_answer(self, selected: str) -> None:
        stat = self.stats[self.current_de]

        if selected == self.correct_en:
            # ---------- SM-2-Update (vereinfacht auf richtig/falsch) -------
            if stat["n"] == 0:
                stat["I"] = 1
            elif stat["n"] == 1:
                stat["I"] = 6
            else:
                stat["I"] = round(stat["I"] * stat["EF"])
            stat["n"] += 1
            stat["due"] = stat["I"]           # nächste Fälligkeit

            # Streak / Level-Logik
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
            # ---------- Fehler -> zurücksetzen ----------------------------
            stat["n"] = 0
            stat["I"] = 1
            stat["EF"] = max(stat["EF"] - 0.2, 1.3)
            stat["due"] = 1                  # sofort nochmal
            self.streak = 0
            self.update_progress()
            self.status_var.set(f"Level {self.level} – 0/{MAX_STREAK} richtige Folge")
            messagebox.showwarning("Falsch",
                                   "Leider falsch! Der Zähler wird zurückgesetzt.")
            self.next_question()

    # --------------------------------------------------------------------- #
    def update_progress(self) -> None:
        self.progress["value"] = self.streak

    # --------------------------------------------------------------------- #
    def speak_word(self) -> None:
        if self.engine:
            self.engine.say(self.current_de)
            self.engine.runAndWait()
        else:
            messagebox.showinfo(
                "Sprachausgabe nicht verfügbar",
                "Für die Aussprache wird das Paket 'pyttsx3' benötigt "
                "(pip install pyttsx3)."
            )

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("450x500")
    root.resizable(False, False)
    VokabelSpiel(root)
    root.mainloop()
