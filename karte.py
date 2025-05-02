# karte.py (mit Text-to-Speech)
from tkinter import Canvas, Toplevel
import pyttsx3

class KartePopup:
    def __init__(self, master, level, station_desc):
        # Neues Fenster für die Karte
        self.window = Toplevel(master)
        self.window.title(f"Level {level} geschafft!")
        self.window.geometry("600x400")
        self.canvas = Canvas(self.window, width=600, height=400, bg="white")
        self.canvas.pack()
        
        # Hier kann bestehende Karten-Rendering-Logik eingebunden werden
        # z.B. self.canvas.create_image(...)

        # Erklärungstext mittig anzeigen
        text = station_desc.get(str(level))
        if text:
            self.canvas.create_text(
                300, 200,  # Fenstermitte
                text=text,
                font=("Arial", 16, "bold"),
                fill="black",
                width=500,
                justify="center",
                tags="desc_text"
            )
            # Text-to-Speech initialisieren und sprechen
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(text)
            engine.runAndWait()
