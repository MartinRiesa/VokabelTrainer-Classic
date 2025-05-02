<<<<<<< HEAD
# station_description.py (aktualisiert)
import csv
import os

class StationDescription:
    """
    Lädt Stationsbeschreibungen (deutsch/englisch) aus CSV-Dateien und stellt sie bereit.
    """
    def __init__(self, language='de'):
        filename = f"Stationenbeschreibung-{language}.csv" if language == 'en' else "Stationenbeschreibung.csv"
        if not os.path.isfile(filename):
            filename = "Stationenbeschreibung.csv"
        self.descriptions = {}
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    keys = {k.lower(): v for k, v in row.items()}
                    station_id = keys.get('stationenid') or keys.get('id') or keys.get('stationid')
                    station_name = keys.get('station') or keys.get('stationname') or keys.get('name')
                    description = keys.get('erklärung') or keys.get('beschreibung') or keys.get('description')
                    if station_id and description:
                        self.descriptions[station_id] = description
                    if station_name and description:
                        self.descriptions[station_name] = description
        except FileNotFoundError:
            print(f"Warnung: Datei '{filename}' für Stationsbeschreibungen nicht gefunden.")

    def get(self, station_id_or_name):
        """
        Gibt die Stationsbeschreibung für die gegebene ID oder den Stationsnamen zurück.
        """
        return self.descriptions.get(station_id_or_name, "")
=======
import pandas as pd
import threading
import tkinter as tk
from config import BASE_PATH, BANNER_W
from overview_controller import show_overview
from level_manager import advance_level

# Pfad zur CSV mit den Stationsbeschreibungen
CSV_DESC = BASE_PATH / "Stationenbeschreibung-englisch.csv"

# Daten beim ersten Laden einlesen und vorbereiten
try:
    df_desc = pd.read_csv(CSV_DESC, sep=';', encoding='utf-8-sig')
    df_desc = df_desc[pd.notnull(df_desc['Nr'])]
    df_desc['Nr'] = df_desc['Nr'].astype(int)
except Exception as e:
    df_desc = None
    print(f"Fehler beim Laden der Stationsbeschreibung: {e}")

def show_description(game):
    if df_desc is None:
        _go_to_overview(game)
        return
    level = game.level
    row = df_desc.loc[df_desc['Nr'] == level]
    if row.empty:
        text = "Keine Beschreibung verfügbar."
    else:
        row = row.iloc[0]
        lang = getattr(game, 'native_lang', None)
        if lang in df_desc.columns:
            text = row.get(lang) or row.get("Erklärung")
        else:
            text = row.get("Erklärung")
    frame = game.canvas.master
    game.desc_label = tk.Label(frame, text=text, wraplength=BANNER_W-20, justify="left")
    game.desc_label.pack(pady=(10,5))
    game.skip_button = tk.Button(frame, text="Überspringen", command=lambda: skip_description(game))
    game.skip_button.pack(pady=(0,10))
    game.skip_desc = False
    def _speak_and_continue():
        game.tts.say(text)
        game.tts.runAndWait()
        if not getattr(game, 'skip_desc', False):
            def finish():
                if hasattr(game, 'desc_label'): game.desc_label.destroy()
                if hasattr(game, 'skip_button'): game.skip_button.destroy()
                _go_to_overview(game)
            game.root.after(0, finish)
    threading.Thread(target=_speak_and_continue, daemon=True).start()

def skip_description(game):
    game.skip_desc = True
    try: game.tts.stop()
    except: pass
    _go_to_overview(game)

def _go_to_overview(game):
    from fragenlogik import next_question
    if hasattr(game, 'desc_label'): game.desc_label.destroy()
    if hasattr(game, 'skip_button'): game.skip_button.destroy()
    show_overview(game)
    success = advance_level(game)
    if success: next_question(game)
>>>>>>> parent of f434f6d (Versuch Text unter Bild)
