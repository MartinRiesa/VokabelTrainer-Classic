# uebersichtskarte.py

import tkinter as tk
from tkinter import Toplevel, Button
from PIL import Image, ImageTk
from hilfsfunktionen import geo_to_pixel
from config import MAP_SMALL, MAP_LARGE, MAP_FILE, TRAIN_ICON

def show_overview(game):
    win = Toplevel(game.root)
    win.title("Übersichtskarte")
    win.grab_set()

    # Karte in groß anzeigen
    map_img = ImageTk.PhotoImage(
        Image.open(MAP_FILE).resize(MAP_LARGE, Image.LANCZOS), master=win
    )
    canvas = tk.Canvas(win, width=MAP_LARGE[0], height=MAP_LARGE[1])
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=map_img)
    win.map_img = map_img  # Referenz halten, damit Bild nicht gelöscht wird

    # Marker für alle Stationen
    for idx, st in enumerate(game.stations):
        x, y = geo_to_pixel(st['lat'], st['lon'],
                             map_w=MAP_LARGE[0], map_h=MAP_LARGE[1])
        if idx == game.level - 1:
            # Aktuelle Station hervorheben
            canvas.create_oval(x-12, y-12, x+12, y+12, outline="red", width=3)
        icon = ImageTk.PhotoImage(Image.open(TRAIN_ICON).resize((24, 24)))
        canvas.create_image(x, y, image=icon)
        win.icon = icon

    # Weiter-Button
    btn = Button(win, text="Weiter", command=win.destroy)
    btn.pack(pady=10)

    win.wait_window()
