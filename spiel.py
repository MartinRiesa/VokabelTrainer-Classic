# spiel.py (aktualisiert)
import tkinter as tk
from karte import KartePopup
from station_description import StationDescription

class Spiel:
    def __init__(self, master, vocab_levels):
        self.master = master
        self.vocab_levels = vocab_levels
        self.level = 1
        # Zentrale Instanz für Stationsbeschreibungen
        self.station_desc = StationDescription(language='de')
        # Initialisiere weitere Spielkomponenten …
        # Beispiel: Canvas, Buttons, Statusanzeigen etc.
    
    def start(self):
        # Startet das Spiel, zeigt erste Level-Ansicht etc.
        pass

    def quiz_antwort(self, richtig):
        # Logik nach jeder Antwort im Quiz…
        if self._level_abgeschlossen():
            self.level_geschafft()
    
    def _level_abgeschlossen(self):
        # Prüft, ob aktuelles Level geschafft ist
        # Rückgabewert True, wenn Level komplett beantwortet
        # Placeholder-Implementierung:
        return True

    def level_geschafft(self):
        """Wird aufgerufen, wenn ein Level erfolgreich abgeschlossen wurde."""
        # Bestehende Logik (Punkte, Statistik, etc.) bleibt erhalten.
        
        # Karte-Popup mit Erklärungstext anzeigen
        KartePopup(self.master, self.level, self.station_desc)
        
        # Anschließend nächstes Level vorbereiten
        self.level += 1
        # Weitere Reset-Logik hier …
