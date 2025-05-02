# stat_model.py

from datetime import datetime, timedelta

class Stat:
    """
    Modelliert den Leitner-Status für eine einzelne Vokabel:
    - n: Anzahl der bisherigen richtigen Antworten
    - i: Index in SPACING_MIN für die nächste Wiederholung
    - due: Datum/Uhrzeit, wann die Karte fällig ist
    - wrong_choices: Liste zuletzt falsch gewählter Distraktoren
    """
    def __init__(self):
        self.n = 0
        self.i = 0
        self.due = datetime.now() + timedelta(minutes=0)
        self.wrong_choices = []

    def to_dict(self):
        """
        Serialisiert das Stat-Objekt in ein JSON-kompatibles Dict.
        """
        return {
            "n": self.n,
            "i": self.i,
            "due": self.due.isoformat(),
            "wrong_choices": self.wrong_choices
        }

    @classmethod
    def from_dict(cls, data):
        """
        Erzeugt ein Stat-Objekt aus einem Dict (z.B. aus JSON).
        """
        obj = cls()
        obj.n = data.get("n", 0)
        obj.i = data.get("i", 0)
        due_str = data.get("due")
        if due_str:
            try:
                obj.due = datetime.fromisoformat(due_str)
            except ValueError:
                obj.due = datetime.now()
        obj.wrong_choices = data.get("wrong_choices", [])
        return obj
