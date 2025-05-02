# level_manager.py

from stats_game import Stat
from tkinter import messagebox
import poster
from geo_utils import geo_to_pixel
from config import MAP_SMALL

def advance_level(game):
    """
    Erhöht das Level, erweitert den Vokabel-Pool, aktualisiert Poster, Blur,
    GUI-Labels und Minikarte.
    """
    # Spielende?
    if game.level >= game.total_levels:
        messagebox.showinfo("Ende", "Alle Stationen geschafft!")
        game.root.quit()
        return False

    # Level hochsetzen
    game.level += 1

    # Vokabel-Pool erweitern
    neue_vocab = game.vocab_levels[game.level - 1]
    game.vocab_pool += neue_vocab
    game.vocab = list(game.vocab_pool)

    # Statistik neu aufbauen
    game.stats = {q: Stat() for q, _ in game.vocab_pool}
    game.streak = 0
    game.last_question = None

    # Poster neu laden (inkl. maximalen Blur)
    poster.load_poster(game, game.level)

    # GUI-Labels aktualisieren
    station_name = game.stations[game.level - 1]['name']
    game.level_var.set(f"Station {game.level}: {station_name}")
    lat, lon = game.stations[game.level - 1]['lat'], game.stations[game.level - 1]['lon']
    game.coord_var.set(f"{lat:.4f}, {lon:.4f}")

    # Minikarte verschieben
    w, h = MAP_SMALL
    x, y = geo_to_pixel(lat, lon, map_w=w, map_h=h)
    game.map_canvas.coords(game.marker, x, y)
    game.root.tk.call('raise', game.map_canvas._w)

    return True
