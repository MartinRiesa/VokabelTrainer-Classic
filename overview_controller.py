# overview_controller.py (mit Debug-Ausgaben)
import os
import tkinter as tk
from tkinter import Toplevel, Button
from PIL import Image, ImageTk
from geo_utils import geo_to_pixel
from config import MAP_LARGE, MAP_FILE, TRAIN_ICON
from station_description import StationDescription

def show_overview(game):
    """ Zeigt die große Übersichtskarte, markiert Stationen und zeigt Erklärungstext. """
    print(f"DEBUG: show_overview aufgerufen für Level {game.level}")
    station_desc = StationDescription(language='de')
    print("DEBUG: station_desc keys:", list(station_desc.descriptions.keys())[:10])
    print("DEBUG: gesuchter Schlüssel:", str(game.level))

    win = Toplevel(game.root)
    win.title("Übersichtskarte")
    win.grab_set()
    win.transient(game.root)

    # Karte im Großformat
    map_img = ImageTk.PhotoImage(
        Image.open(MAP_FILE).resize(MAP_LARGE, Image.LANCZOS),
        master=win
    )
    canvas = tk.Canvas(win, width=MAP_LARGE[0], height=MAP_LARGE[1], highlightthickness=0)
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=map_img)
    win.map_img = map_img  # Referenz halten

    # Marker setzen
    for idx, st in enumerate(game.stations[:game.level]):
        x, y = geo_to_pixel(st['lat'], st['lon'], map_w=MAP_LARGE[0], map_h=MAP_LARGE[1])
        if idx < game.level - 1:
            r = 6
            canvas.create_oval(x-r, y-r, x+r, y+r, fill="black", outline="")
        else:
            icon = ImageTk.PhotoImage(
                Image.open(TRAIN_ICON).resize((32, 32), Image.LANCZOS),
                master=win
            )
            canvas.create_image(x, y, image=icon)
            win.icons = getattr(win, 'icons', []) + [icon]

    # Weiter-Button
    cx = MAP_LARGE[0] // 2
    cy = MAP_LARGE[1] // 2
    weiter_btn = Button(win, text="Weiter", width=15, command=win.destroy)
    canvas.create_window(cx, cy, window=weiter_btn)

    # Erklärungstext mittig anzeigen
    text = station_desc.get(str(game.level))
    print("DEBUG: gefundener Text:", repr(text))
    if text:
        canvas.create_text(
            cx,
            cy + 40,
            text=text,
            font=("Arial", 16, "bold"),
            fill="blue",
            width=MAP_LARGE[0] - 100,
            justify="center",
            tags="desc_text"
        )

    win.wait_window()
