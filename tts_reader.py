# tts_reader.py
"""
Einfacher Wrapper für die asynchrone Text‑to‑Speech‑Ausgabe.
Verwendet die bestehende tts_engine.py‑Initialisierung, damit eine einzige
Engine‑Instanz pro Prozess genutzt wird.
"""

import threading
from tts_engine import init_tts

_ENGINE = None
_LOCK = threading.Lock()

def _get_engine():
    global _ENGINE
    with _LOCK:
        if _ENGINE is None:
            _ENGINE = init_tts()
        return _ENGINE

def _speak(engine, text: str):
    if not text:
        return
    engine.say(text)
    engine.runAndWait()

def speak_async(text: str):
    """
    Gibt `text` per TTS wieder, ohne den GUI‑Thread zu blockieren.
    """
    if not text:
        return
    engine = _get_engine()
    threading.Thread(target=_speak, args=(engine, text), daemon=True).start()