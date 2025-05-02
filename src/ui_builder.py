# ui_builder.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from config import BANNER_W, BANNER_H, MAP_SMALL, MAP_FILE, TRAIN_ICON

def build_window(game):
    game.root = tk.Tk()
    game.root.title("Vokabellernspiel – Deutschland-Reise")
    game.root.geometry("1024x860")
    game.root.configure(bg="#eef4fb")

def build_banner(game):
    frame = ttk.Frame(game.root, padding=10, style="Bg.TFrame")
    frame.pack()
    game.canvas = tk.Canvas(frame, width=BANNER_W, height=BANNER_H, bg="#ccc")
    game.canvas.create_text(BANNER_W//2, BANNER_H//2, text="Poster hier", font=("Arial",24), fill="#666")
    game.canvas.pack()
    game.poster_item = game.canvas.create_image(0,0,anchor="nw")

def build_info_row(game):
    frame = ttk.Frame(game.root, padding=10, style="Bg.TFrame")
    frame.pack(fill="x")
    game.level_var = tk.StringVar()
    ttk.Label(frame, textvariable=game.level_var, font=("Arial",16), style="Bg.TLabel").pack(side="left", padx=12)
    game.coord_var = tk.StringVar()
    ttk.Label(frame, textvariable=game.coord_var, font=("Arial",14), style="Bg.TLabel").pack(side="left", padx=12)

def build_quiz_area(game):
    frame = ttk.Frame(game.root, padding=10, style="Bg.TFrame")
    frame.pack(expand=True, fill="both")
    # Frage
    game.qvar = tk.StringVar()
    qr = ttk.Frame(frame, style="Bg.TFrame"); qr.pack(pady=(30,15))
    ttk.Label(qr, textvariable=game.qvar, font=("Arial",28,"bold"), style="Bg.TLabel").pack(side="left")
    # ...
    # Buttons und next_btn hier anlegen

def build_minimap(game):
    widget = tk.Canvas(game.root, width=MAP_SMALL[0], height=MAP_SMALL[1], highlightthickness=1)
    widget.pack(pady=10)
    # Bild und Marker laden
    game.map_canvas = widget

def build_ui(game):
    build_window(game)
    build_banner(game)
    build_info_row(game)
    build_quiz_area(game)
    build_minimap(game)
