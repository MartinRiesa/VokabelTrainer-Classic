# spiel.py

import tkinter as tk
from tkinter import messagebox
import initialisierung
import fragenlogik
from tts import init_tts

class Spiel:
    def __init__(self, root):
        self.root = root

        # 1) TTS-Engine initialisieren
        self.tts = init_tts()

        # 2) Erstmalige Sprachauswahl und Spieldaten laden
        self._ask_language()
        stations, vocab_levels = initialisierung.load_game_data(self.learn_lang, self.native_lang)

        # 3) Spielzustand initialisieren
        if not initialisierung.init_game_state(self, stations, vocab_levels):
            return

        # 4) GUI aufbauen
        initialisierung.build_ui(self)

        # 5) Erstes Poster laden und erste Frage starten
        initialisierung.poster.load_poster(self, self.level)
        fragenlogik.next_question(self)

    def _ask_language(self):
        """
        Zeigt ein modales Fenster zur Wahl von Lern- und Muttersprache.
        Erkennt Sprachen automatisch aus der CSV-Kopfzeile.
        Speichert self.learn_lang und self.native_lang.
        """
        from config import CSV_VOCAB
        import pandas as pd

        df = pd.read_csv(CSV_VOCAB, sep=';', nrows=0, encoding='utf-8-sig')
        languages = list(df.columns)

        win = tk.Toplevel(self.root)
        win.title("Sprachauswahl")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="Lernsprache:").pack(padx=10, pady=(10, 0))
        learn_var = tk.StringVar(value=languages[0])
        tk.OptionMenu(win, learn_var, *languages).pack(padx=10, pady=5)

        tk.Label(win, text="Muttersprache:").pack(padx=10, pady=(10, 0))
        native_var = tk.StringVar(value=languages[1] if len(languages) > 1 else languages[0])
        tk.OptionMenu(win, native_var, *languages).pack(padx=10, pady=5)

        def on_ok():
            if learn_var.get() == native_var.get():
                messagebox.showerror("Fehler", "Lern- und Muttersprache müssen unterschiedlich sein.")
                return
            self.learn_lang = learn_var.get()
            self.native_lang = native_var.get()
            win.destroy()

        tk.Button(win, text="OK", command=on_ok).pack(pady=15)
        self.root.wait_window(win)

    def change_language(self):
        """
        Schaltet zurück zur Sprachwahl und startet das Spiel komplett neu.
        """
        # Alte Widgets entfernen
        for widget in self.root.winfo_children():
            widget.destroy()

        # Sprachauswahl erneut anzeigen
        self._ask_language()
        stations, vocab_levels = initialisierung.load_game_data(self.learn_lang, self.native_lang)

        # Spielzustand neu initialisieren
        if not initialisierung.init_game_state(self, stations, vocab_levels):
            return

        # GUI neu aufbauen
        initialisierung.build_ui(self)

        # Erstes Poster laden und Quiz starten
        initialisierung.poster.load_poster(self, self.level)
        fragenlogik.next_question(self)
