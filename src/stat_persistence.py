# stat_persistence.py

import json
from pathlib import Path
from stat_model import Stat

STATS_FILE = Path(__file__).resolve().parent / "stats.json"

def save_stats(game):
    """
    Speichert alle Stat-Objekte aus game.stats in eine JSON-Datei.
    """
    data = {q: stat.to_dict() for q, stat in game.stats.items()}
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_stats(game):
    """
    Lädt Stat-Objekte aus der JSON-Datei und schreibt sie nach game.stats.
    Wenn keine Datei existiert, passiert nichts.
    """
    if not STATS_FILE.exists():
        return
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    for q, stat_dict in data.items():
        game.stats[q] = Stat.from_dict(stat_dict)
