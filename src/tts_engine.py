# tts_engine.py

import pyttsx3

def init_tts():
    """
    Initialisiert und konfiguriert die TTS-Engine.
    Gibt die Engine-Instanz zurück.
    """
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)    # Sprechgeschwindigkeit
    engine.setProperty('volume', 1.0)  # Lautstärke
    return engine
