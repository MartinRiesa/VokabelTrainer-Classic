# initialisierung.py (aktualisiert)
# --- Bestehender Inhalt bleibt unverändert ---
# (Bitte füge diesen Abschnitt unten in deine originale initialisierung.py ein)

def load_vocab_levels():
    """
    Gibt die geladenen Vokabel-Level-Daten zurück.
    Nutzt die bestehende Variable `vocab_levels`, die in diesem Modul definiert sein muss.
    """
    try:
        return vocab_levels
    except NameError:
        raise RuntimeError("Variable 'vocab_levels' ist nicht definiert. Bitte überprüfe, ob initialisierung.py die Vokabel-Level korrekt lädt und in `vocab_levels` ablegt.")
