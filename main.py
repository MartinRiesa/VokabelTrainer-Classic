# main.py (aktualisiert)
import tkinter as tk
import initialisierung
from spiel import Spiel

def main():
    # Hauptfenster erstellen
    root = tk.Tk()
    root.title("VokabelTrainer Classic")
    
    # Stationen und Vokabel-Level laden
    stations, vocab_levels = initialisierung.load_game_data()
    
    # Spiel-Instanz mit vocab_levels erstellen
    app = Spiel(root, vocab_levels)
    
    # Spielzustand initialisieren (Stationen, Levels etc.)
    initialisierung.init_game_state(app, stations, vocab_levels)
    
    # Starte Spiel-Logik
    app.start()
    
    # Hauptschleife starten
    root.mainloop()

if __name__ == "__main__":
    main()
