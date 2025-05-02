"""Text‑to‑Speech (Microsoft SAPI, NSSpeechSynthesizer, eSpeak …) wrapper for VokabelTrainer‑Classic.
Benötigt:  `pip install pyttsx3` (und unter Windows zusätzlich `pypiwin32`).
Verwende   `from tts_engine import speak`   um Text laut vorlesen zu lassen.
"""

import pyttsx3
from threading import Lock

_lock = Lock()
_engine = None

def _init_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        # Grundeinstellungen
        _engine.setProperty("rate", 160)      # Wörter pro Minute
        _engine.setProperty("volume", 1.0)    # 0.0 – 1.0
        # Versuche, eine deutsche Stimme zu wählen
        for v in _engine.getProperty("voices"):
            if 'de' in v.id.lower() or 'german' in v.name.lower():
                _engine.setProperty('voice', v.id)
                break
    return _engine

def speak(text: str) -> None:
    """Synchrones Vorlesen des übergebenen Textes."""
    if not text:
        return
    with _lock:
        engine = _init_engine()
        engine.stop()      # evtl. vorherige Ausgabe abbrechen
        engine.say(text)
        engine.runAndWait()
