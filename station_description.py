import csv
import os

class StationDescription:
    """
    Lädt die Stationsbeschreibungen (deutsch oder englisch) aus CSV-Dateien
    und bietet Zugriff per Stations-ID oder Stationsname.
    """
    def __init__(self, language='de'):
        # Versuche, die CSV für die gewählte Sprache zu laden.
        # Falls nicht vorhanden, lade die deutsche CSV.
        filename = f"Stationenbeschreibung-{language}.csv" if language == 'en' else "Stationenbeschreibung.csv"
        if not os.path.isfile(filename):
            filename = "Stationenbeschreibung.csv"
        self.descriptions = {}  # Mapping: ID oder Name -> Beschreibungstext
        
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                # Hier wird angenommen, dass die CSV Spalten für ID, Name, Beschreibung hat.
                # Der Delimiter kann je nach CSV ',' oder ';' sein.
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    # Vereinheitliche die Spaltennamen (in Kleinbuchstaben)
                    keys = {k.lower(): v for k, v in row.items()}
                    # Mögliche Schlüsselnamen ermitteln
                    station_id = keys.get('stationenid') or keys.get('id') or keys.get('stationid')
                    station_name = keys.get('station') or keys.get('stationname') or keys.get('name')
                    description = keys.get('beschreibung') or keys.get('description')
                    # Speichere Zuordnung (z.B. nach ID und/oder Name)
                    if station_id and description:
                        self.descriptions[station_id] = description
                    if station_name and description:
                        # Optional: auch nach Name zugänglich machen
                        self.descriptions[station_name] = description
        except FileNotFoundError:
            print(f"Warnung: Datei '{filename}' für Stationsbeschreibungen nicht gefunden.")
    
    def get(self, station_id_or_name):
        """
        Gibt die Stationsbeschreibung für die gegebene ID oder den Stationsnamen zurück.
        Liefert leeren String, falls nichts gefunden wird.
        """
        return self.descriptions.get(station_id_or_name, "")
