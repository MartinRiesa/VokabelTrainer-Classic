from pathlib import Path

BASE_PATH      = Path(__file__).resolve().parent
CSV_STATIONS   = BASE_PATH / "Stationenbeschreibung-englisch.csv"
EXCEL_VOCAB    = BASE_PATH / "Vokabeln alle.csv"
MAP_FILE       = BASE_PATH / "germany_map.png"
TRAIN_ICON     = BASE_PATH / "train.png"
CURTAIN_FILE   = BASE_PATH / "Vorhang.png"

BANNER_W, BANNER_H = 960, 360
MAP_SMALL          = (200, 200)
MAP_LARGE          = (1024, 860)

STREAK_GOAL  = 10
SPACING_MIN  = (1, 10, 60, 720, 1440, 4320)
DOT_RADIUS   = 4

LAT_MIN, LAT_MAX = 47.3, 55.1
LON_MIN, LON_MAX = 5.9, 15.2

CSV_VOCAB = BASE_PATH / "Vokabeln alle.csv"
