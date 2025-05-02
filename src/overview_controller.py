# overview_controller.py

import os
import tkinter as tk
from tkinter import Toplevel, Button
from PIL import Image, ImageTk
from geo_utils import geo_to_pixel
from config import MAP_LARGE, MAP_FILE, TRAIN_ICON

def show_overview(game):
    """
    Zeigt die große Übersichtskarte in einem modalen Fenster,
    markiert alle bereits abgeschlossenen Stationen mit Punkten,
    hebt die aktuelle Station mit einem Zug-Icon hervor
    und zeigt den 'Weiter'-Button in der Kartenmitte an.
    """
    win = Toplevel(game.root)
    win.title("Übersichtskarte")
    win.grab_set()
    win.transient(game.root)

    # 1) Karte im Großformat
    map_img = ImageTk.PhotoImage(
        Image.open(MAP_FILE).resize(MAP_LARGE, Image.LANCZOS),
        master=win
    )
    canvas = tk.Canvas(win, width=MAP_LARGE[0], height=MAP_LARGE[1], highlightthickness=0)
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=map_img)
    win.map_img = map_img  # Referenz halten

    # 2) Marker: abgeschlossene Stationen als Punkt, aktuelle Station mit Zug-Icon
    for idx, st in enumerate(game.stations[:game.level]):
        x, y = geo_to_pixel(
            st['lat'], st['lon'],
            map_w=MAP_LARGE[0], map_h=MAP_LARGE[1]
        )
        if idx < game.level - 1:
            # bereits abgeschlossen: kleiner schwarzer Punkt
            r = 6
            canvas.create_oval(x-r, y-r, x+r, y+r, fill="black", outline="")
        else:
            # aktuelle Station: Zug-Icon
            icon = ImageTk.PhotoImage(
                Image.open(TRAIN_ICON).resize((32, 32), Image.LANCZOS),
                master=win
            )
            canvas.create_image(x, y, image=icon)
            if not hasattr(win, 'icons'):
                win.icons = []
            win.icons.append(icon)

    # 3) "Weiter"-Button in der Kartenmitte als Canvas-Widget
    weiter_btn = Button(win, text="Weiter", width=15, command=win.destroy)
    # Position in der Mitte der Canvas
    cx = MAP_LARGE[0] // 2
    cy = MAP_LARGE[1] // 2
    canvas.create_window(cx, cy, window=weiter_btn)

    # 4) blockierend bis Klick
    win.wait_window()
