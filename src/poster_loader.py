# src/poster_loader.py

import os
from PIL import Image, ImageTk
import tkinter as tk

def load_poster_image(path, size):
    """
    Lädt und skaliert das Bild auf die gewünschte Größe.
    """
    img = Image.open(path)
    img = img.resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)

def display_poster(game, photo_image):
    """
    Zeigt das Poster und unterhalb den Erklärungstext an.
    """
    # Alte Widgets entfernen
    if hasattr(game, 'poster_label'):
        game.poster_label.destroy()
    if hasattr(game, 'explanation_label'):
        game.explanation_label.destroy()

    # Poster anzeigen
    game.poster_label = tk.Label(game.root, image=photo_image)
    game.poster_label.image = photo_image
    game.poster_label.pack(pady=(10, 0))

    # Erklärungstext
    try:
        text = game.stations.loc[game.level - 1, 'Erklärung']
    except Exception:
        text = ""
    game.explanation_label = tk.Label(
        game.root,
        text=text,
        wraplength=800,
        justify='center'
    )
    game.explanation_label.pack(pady=(5, 20))

def clear_poster(game):
    """
    Entfernt Poster- und Erklärungselemente.
    """
    if hasattr(game, 'poster_label'):
        game.poster_label.destroy()
        del game.poster_label
    if hasattr(game, 'explanation_label'):
        game.explanation_label.destroy()
        del game.explanation_label

def display_placeholder(game, message):
    """
    Zeigt eine graue Fläche mit Hinweistext.
    """
    clear_poster(game)
    placeholder = tk.Label(game.root, text=message, bg='#ccc', width=80, height=10)
    placeholder.pack(pady=(20, 20))
    game.poster_label = placeholder
