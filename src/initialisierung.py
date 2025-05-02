# src/initialisierung.py

import os
import pandas as pd
from PIL import Image, ImageTk
import poster_loader as poster

# Pfade zu den CSV-Dateien im assets/data-Verzeichnis
CSV_VOCAB = os.path.join("assets", "data", "Vokabeln alle.csv")
CSV_STATIONS = os.path.join("assets", "data", "Stationenbeschreibung-englisch.csv")

def load_game_data(learn_lang: str, native_lang: str):
    df_vocab = pd.read_csv(CSV_VOCAB, sep=';', encoding='utf-8-sig')
    df_st = pd.read_csv(CSV_STATIONS, sep=';', encoding='utf-8-sig')
    vocab_levels = df_vocab[[learn_lang, native_lang]]
    stations = df_st
    return stations, vocab_levels

def init_game_state(app, stations, vocab_levels):
    try:
        app.level = 1
        app.questions = vocab_levels.values.tolist()
        app.current_question = 0
        # halte die stations-Daten in der Game-Instanz, damit display_poster darauf zugreifen kann
        app.stations = stations
        return True
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Fehler", f"Spiel konnte nicht initialisiert werden:\n{e}")
        return False

def build_ui(app):
    app.root.title("Vokabellernspiel")
    # ... sonst unverändert ...

def load_poster(app, level):
    """
    Lädt das Poster für das aktuelle Level und zeigt es an.
    Nutzt dazu den Spaltennamen 'Bilddatei' in Deiner Stations-CSV.
    """
    # Lies aus der Stations-DataFrame den Dateinamen der Bildspalte
    try:
        filename = app.stations.loc[level - 1, 'Bilddatei']
    except KeyError:
        # Falls Deine CSV-Spalte anders heißt, passe hier den Spaltennamen an!
        filename = None

    if filename:
        poster_path = os.path.join("assets", "images", filename)
        if os.path.exists(poster_path):
            # lade und zeige Bild + Erklärung
            photo = poster.load_poster_image(poster_path, (800, 400))
            poster.display_poster(app, photo)
            return

    # Fallback, falls kein Bild gefunden:
    poster.clear_poster(app)
    poster.display_placeholder(app, f"Kein Poster für Level {level}")
