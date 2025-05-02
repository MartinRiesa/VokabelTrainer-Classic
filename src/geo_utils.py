# geo_utils.py

from config import LAT_MIN, LAT_MAX, LON_MIN, LON_MAX

def geo_to_pixel(lat, lon, map_w, map_h):
    """
    Wandelt geographische Koordinaten (lat, lon) in Pixelkoordinaten
    auf einer Karte der Größe (map_w, map_h) um.
    Die Konfiguration LAT_MIN/MAX und LON_MIN/MAX definiert den Kartenbereich.
    """
    # Normieren auf [0..1]
    x_norm = (lon - LON_MIN) / (LON_MAX - LON_MIN)
    y_norm = 1 - (lat - LAT_MIN) / (LAT_MAX - LAT_MIN)
    # Auf Pixelgröße skalieren
    x = int(x_norm * map_w)
    y = int(y_norm * map_h)
    return x, y

def clamp(value, min_value, max_value):
    """
    Beschränkt `value` auf den Bereich [min_value, max_value].
    """
    return max(min_value, min(value, max_value))
