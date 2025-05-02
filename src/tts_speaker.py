# tts_speaker.py

import threading
from tts_engine import init_tts as _init_tts
from tts_engine import init_tts

def speak_text(engine, text):
    """
    Spricht `text` mit der gegebenen TTS-Engine.
    """
    engine.say(text)
    engine.runAndWait()

def speak_current_word(game):
    """
    Spricht das aktuell angezeigte Wort aus `game.current_question`.
    Führt die Sprachausgabe in einem separaten Thread aus.
    """
    text = getattr(game, "current_question", None)
    if text:
        # Wenn Engine noch nicht existiert, initialisieren
        if not hasattr(game, 'tts') or game.tts is None:
            game.tts = init_tts()
        threading.Thread(target=speak_text, args=(game.tts, text), daemon=True).start()
