# src/poster_loader.py

import os
from PIL import Image, ImageTk
import tkinter as tk

def load_poster_image(path, size):
    """
    Lädt das Posterbild vom Dateisystem und skaliert es auf die gewünschte Größe.
    """
    img = Image.open(path)
    img = img.resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)

def display_poster(game, photo_image):
    """
    Zeigt das Poster sowie die zugehörige Erklärung unterhalb des Bildes an.
    game: Instanz der Spiel-Klasse mit Attributen 'root', 'stations' (DataFrame) und 'level'.
    photo_image: Tkinter-kompatibles PhotoImage-Objekt des Posters.
    """
    # Vorherige Poster- und Text-Widgets entfernen, falls vorhanden
    if hasattr(game, 'poster_label'):
        game.poster_label.destroy()
    if hasattr(game, 'explanation_label'):
        game.explanation_label.destroy()

    # Poster anzeigen
    game.poster_label = tk.Label(game.root, image=photo_image)
    game.poster_label.image = photo_image
    game.poster_label.pack(pady=(10, 0))

    # Erklärungstext aus dem DataFrame holen (Spalte 'Erklärung')
    try:
        explanation = game.stations.iloc[game.level - 1]['Erklärung']
    except Exception:
        explanation = ""

    # Erklärung unterhalb des Bildes anzeigen
    game.explanation_label = tk.Label(
        game.root,
        text=explanation,
        wraplength=800,      # Zeilenumbruch bei 800px
        justify='center'     # Zentrierter Text
    )
    game.explanation_label.pack(pady=(5, 10))
