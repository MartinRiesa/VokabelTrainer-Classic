# station_description.py (sicherstellen vorhanden)
import csv
import os

class StationDescription:
    """
    Lädt Stationsbeschreibungen (deutsch/englisch) aus CSV-Dateien und stellt sie bereit.
    """
    def __init__(self, language='de'):
        filename = f"Stationenbeschreibung-{language}.csv" if language == 'en' else "Stationenbeschreibung.csv"
        if not os.path.isfile(filename):
            filename = "Stationenbeschreibung.csv"
        self.descriptions = {}
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    keys = {k.lower(): v for k, v in row.items()}
                    # ID oder Name
                    station_id = keys.get('stationenid') or keys.get('id') or keys.get('stationid')
                    station_name = keys.get('station') or keys.get('stationname') or keys.get('name')
                    description = keys.get('erklärung') or keys.get('beschreibung') or keys.get('description')
                    if station_id and description:
                        self.descriptions[station_id] = description
                    if station_name and description:
                        self.descriptions[station_name] = description
        except FileNotFoundError:
            print(f"Warnung: Datei '{filename}' für Stationsbeschreibungen nicht gefunden.")

    def get(self, station_id_or_name):
        """
        Gibt die Stationsbeschreibung für die gegebene ID oder den Stationsnamen zurück.
        """
        return self.descriptions.get(station_id_or_name, "")
