#!/usr/bin/env python3
"""
Einfaches Vokabel-Lernspiel (Konsole)

Level-Regeln
------------
• Level 1:  7 Vokabeln  
• Level 2: 14 Vokabeln (Level 1 + 7 neue)  
• Level 3: 21 Vokabeln (alle)

Ziel pro Level: 10 richtige Antworten in Folge.  
Bei Fehler ⇒ Zähler 0 und Level von vorn.
"""

import random
import sys

# --- 1. Feste Vokabelliste ---------------------------------------------------
VOCAB = [
    ("Apfel", "apple"),     ("Haus", "house"),     ("Hund", "dog"),
    ("Katze", "cat"),       ("Stuhl", "chair"),    ("Buch", "book"),
    ("Baum", "tree"),       ("Wasser", "water"),   ("Tisch", "table"),
    ("Auto", "car"),        ("Stadt", "city"),     ("Freund", "friend"),
    ("Schule", "school"),   ("Brot", "bread"),     ("Ball", "ball"),
    ("Sonne", "sun"),       ("Mond", "moon"),      ("Fisch", "fish"),
    ("Milch", "milk"),      ("Straße", "street"),  ("Zeit", "time"),
]

# --- 2. Hilfsfunktionen ------------------------------------------------------
def frage_stellen(level_vocab):
    """Eine deutsche Vokabel fragen und vier englische Antworten liefern."""
    deutsch, korrekt = random.choice(level_vocab)

    # Drei falsche Antworten ziehen
    falsche = [en for de, en in level_vocab if en != korrekt]
    anzeigen = random.sample(falsche, 3) + [korrekt]
    random.shuffle(anzeigen)

    # Ausgabe
    print(f"\nWas heißt „{deutsch}“ auf Englisch?")
    for idx, option in enumerate(anzeigen, 1):
        print(f"  {idx}) {option}")

    # Eingabe & Validierung
    while True:
        wahl = input("Deine Wahl (1-4): ").strip()
        if wahl in {"1", "2", "3", "4"}:
            return anzeigen[int(wahl) - 1] == korrekt
        print("Bitte 1–4 eingeben.")

def spiele_level(von, bis, level_nr):
    """Spielt ein Level; gibt True zurück, wenn bestanden."""
    level_vocab = VOCAB[von:bis]
    print(f"\n=== Level {level_nr} – {len(level_vocab)} Vokabeln ===")
    streak = 0

    while streak < 10:
        if frage_stellen(level_vocab):
            streak += 1
            print(f"Richtig! ({streak}/10 in Folge)")
        else:
            print("Leider falsch – der Zähler wird zurückgesetzt.")
            streak = 0
    return True

# --- 3. Hauptprogramm --------------------------------------------------------
def main():
    level_slices = [(0, 7), (0, 14), (0, 21)]

    for nr, (start, stop) in enumerate(level_slices, 1):
        bestanden = spiele_level(start, stop, nr)
        if not bestanden:          # aktuell nie False, aber offen für Erweiterung
            print("Spiel beendet.")
            sys.exit()
        print(f"Level {nr} geschafft!\n")

    print("🎉 Herzlichen Glückwunsch – alle Level abgeschlossen! 🎉")

if __name__ == "__main__":
    main()
