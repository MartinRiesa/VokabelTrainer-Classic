# game_state.py
from tkinter import messagebox
from stats_game import Stat

def init_game_state(game, stations, vocab_levels):
    if not stations:
        messagebox.showerror("Fehler", "Keine Stationen gefunden.")
        game.root.quit()
        return False

    game.stations       = stations
    game.vocab_levels   = vocab_levels
    game.total_levels   = len(vocab_levels)
    game.level          = 1
    game.vocab_pool     = list(vocab_levels[0])
    game.vocab          = list(game.vocab_pool)
    game.stats          = {q: Stat() for q, _ in game.vocab_pool}
    game.streak         = 0
    game.last_question  = None
    return True
