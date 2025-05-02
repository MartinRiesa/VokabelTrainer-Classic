# initialisierung.py

import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from config import (
    BASE_PATH,
    CSV_STATIONS,
    CSV_VOCAB,
    BANNER_W, BANNER_H,
    MAP_FILE, TRAIN_ICON,
    MAP_SMALL
)
from geo_utils import geo_to_pixel
import poster
import fragenlogik


def load_game_data(learn_lang=None, native_lang=None):
    """
    Lädt Stationen und Vokabeln aus Excel/CSV.
    Wenn learn_lang/native_lang angegeben, nutzt es diese Spalten.
    """
    # Stationen laden (Excel)
    df_st = pd.read_csv(CSV_STATIONS, sep=';', header=0, encoding='utf-8-sig')
    stations = []
    for _, row in df_st.iterrows():
        try:
            lat = float(row['Latitude']) / 10000
            lon = float(row['Longitude']) / 10000
            name = str(row['Station'])
            stations.append({"name": name, "lat": lat, "lon": lon})
        except Exception:
            continue

    # Vokabeln laden (CSV)
    df_vocab = pd.read_csv(CSV_VOCAB, sep=';', header=0, encoding='utf-8-sig')
    if learn_lang in df_vocab.columns and native_lang in df_vocab.columns:
        q_col, a_col = learn_lang, native_lang
    else:
        cols = list(df_vocab.columns)
        q_col, a_col = cols[0], cols[1]
    pairs = list(zip(df_vocab[q_col].astype(str), df_vocab[a_col].astype(str)))

    total_levels = len(pairs) // 7
    vocab_levels = [pairs[i*7:(i+1)*7] for i in range(total_levels)]

    return stations, vocab_levels


def init_game_state(game, stations, vocab_levels):
    """
    Initialisiert Spielzustand: Level, Pools, Statistiken.
    """
    game.total_levels = len(vocab_levels)
    game.stations = stations
    game.vocab_levels = vocab_levels

    if not stations:
        messagebox.showerror("Fehler", "Keine Stationen gefunden.")
        game.root.quit()
        return False

    game.level = 1
    game.vocab_pool = list(vocab_levels[0])
    game.vocab = list(game.vocab_pool)

    from stats_game import Stat
    game.stats = {q: Stat() for q, _ in game.vocab_pool}
    game.streak = 0
    game.last_question = None

    return True


def build_ui(game):
    """
    Baut GUI auf: Banner, Infozeile, Quiz, Minikarte, Sprachwechsel-Button.
    """
    # Hauptfenster
    game.root.title("Vokabellernspiel – Deutschland-Reise")
    game.root.geometry("1024x860")
    game.root.configure(bg="#eef4fb")

    # Banner-Canvas
    banner_frame = ttk.Frame(game.root, padding=10)
    banner_frame.pack()
    game.canvas = tk.Canvas(banner_frame, width=BANNER_W, height=BANNER_H, bg="#ccc", highlightthickness=0)
    game.canvas.create_text(BANNER_W//2, BANNER_H//2, text="Poster hier", font=("Arial", 24), fill="#666")
    game.canvas.pack()
    game.poster_item = game.canvas.create_image(0, 0, anchor="nw")

    # Infozeile mit Level, Koordinaten und Sprachwechsel
    info_frame = ttk.Frame(game.root, padding=5)
    info_frame.pack(fill="x")
    game.level_var = tk.StringVar()
    ttk.Label(info_frame, textvariable=game.level_var, font=("Arial", 14, "bold")).pack(side="left", padx=8)
    game.coord_var = tk.StringVar()
    ttk.Label(info_frame, textvariable=game.coord_var, font=("Arial", 12)).pack(side="left", padx=8)

    # Sprachwechsel-Button
    switch_btn = ttk.Button(info_frame, text="Sprache wählen", command=lambda: game.change_language())
    switch_btn.pack(side="right", padx=8)

    # Quiz-Bereich
    play_frame = ttk.Frame(game.root, padding=10)
    play_frame.pack(expand=True, fill="both")
    game.qvar = tk.StringVar()
    qrow = ttk.Frame(play_frame); qrow.pack(pady=(30,15))
    ttk.Label(qrow, textvariable=game.qvar, font=("Arial", 28, "bold")).pack(side="left")
    from tts import speak_current_word
    ttk.Button(qrow, text="🔊", width=3, command=lambda: speak_current_word(game)).pack(side="left", padx=5)

    game.btns = []
    for _ in range(4):
        btn = ttk.Button(play_frame, text="", width=20)
        btn.pack(pady=6)
        game.btns.append(btn)

    # Weiter-Button (wird dynamisch bei Falschantwort eingeblendet)
    game.next_btn = ttk.Button(play_frame, text="Weiter", command=lambda: fragenlogik.next_question(game))

    # Minikarte
    w_small, h_small = MAP_SMALL
    game.map_canvas = tk.Canvas(game.root, width=w_small, height=h_small, highlightthickness=1)
    game.map_canvas.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
    from PIL import Image
    game.map_tk = ImageTk.PhotoImage(
        Image.open(MAP_FILE).resize((w_small, h_small), Image.LANCZOS),
        master=game.root
    )
    game.map_canvas.create_image(0, 0, anchor="nw", image=game.map_tk)
    game.train_tk = ImageTk.PhotoImage(
        Image.open(TRAIN_ICON).convert("RGBA").resize((24, 24), Image.LANCZOS),
        master=game.root
    )
    x0, y0 = geo_to_pixel(game.stations[0]['lat'], game.stations[0]['lon'], map_w=w_small, map_h=h_small)
    game.marker = game.map_canvas.create_image(x0, y0, anchor="center", image=game.train_tk)
