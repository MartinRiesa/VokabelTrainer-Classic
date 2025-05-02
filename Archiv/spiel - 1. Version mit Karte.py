#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vokabellernspiel „Deutschland-Reise“ – vollständige, lauffähige Version
"""

import random, datetime as dt
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pandas as pd

# -------------------- Konfiguration ----------------------------
BASE_PATH      = Path(__file__).resolve().parent
EXCEL_STATIONS = BASE_PATH / "leveltabelle.xlsx"
EXCEL_VOCAB    = BASE_PATH / "englisch.xlsx"
MAP_FILE       = BASE_PATH / "germany_map.png"
TRAIN_ICON     = BASE_PATH / "train.png"
CURTAIN_FILE   = BASE_PATH / "Vorhang.png"

BANNER_W, BANNER_H = 960, 360
MAP_W, MAP_H       = 200, 200
STREAK_GOAL        = 10
SPACING_MIN        = (1, 10, 60, 720, 1440, 4320)
DOT_RADIUS         = 4

LAT_MIN, LAT_MAX = 47.3, 55.1
LON_MIN, LON_MAX = 5.9, 15.2

# -------------------- Datenstrukturen --------------------------
class Stat:
    def __init__(self):
        self.EF, self.n, self.i = 2.5, 0, 1
        self.due = dt.datetime.now()

# -------------------- Hauptklasse ------------------------------
class Spiel:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Vokabellernspiel – Deutschlandreise")
        root.geometry("1024x860")
        root.configure(bg="#eef4fb")

        # 1) Stationen
        df_st = pd.read_excel(EXCEL_STATIONS, header=None)
        self.stations = []
        for latlon, name in zip(df_st.iloc[1:, 2], df_st.iloc[1:, 3]):
            try:
                lat, lon = map(float, str(latlon).split(","))
                self.stations.append({"name": str(name), "lat": lat, "lon": lon})
            except ValueError:
                continue
        if not self.stations:
            messagebox.showerror("Fehler", "Keine Stationen gefunden."); root.quit(); return

        # 2) Vokabeln
        df_v = pd.read_excel(EXCEL_VOCAB, usecols=[0, 1], header=None)
        rows = list(zip(df_v[0].astype(str), df_v[1].astype(str)))
        blocks = len(rows) // 7
        self.total_levels = min(len(self.stations), blocks)
        self.stations = self.stations[:self.total_levels]
        self.vocab_levels = [rows[i*7:(i+1)*7] for i in range(self.total_levels)]

        # 3) Startzustand
        self.level = 1
        self.vocab = self.vocab_levels[0]
        self.stats = {de: Stat() for de, _ in self.vocab}
        self.streak = 0

        # 4) Banner
        banner_fr = ttk.Frame(root, padding=10, style="Bg.TFrame"); banner_fr.pack()
        self.canvas = tk.Canvas(banner_fr, width=BANNER_W, height=BANNER_H, highlightthickness=0)
        self.canvas.pack()
        self.poster_item = self.canvas.create_image(0, 0, anchor="nw")
        self.curtain_full = Image.open(CURTAIN_FILE).convert("RGBA").resize((BANNER_W, BANNER_H), Image.LANCZOS)
        self.curtain_img  = ImageTk.PhotoImage(self.curtain_full, master=root)
        self.curtain_item = self.canvas.create_image(0, 0, anchor="nw", image=self.curtain_img)
        self.curtain_offset = 0

        # 5) Infozeile
        info = ttk.Frame(root, padding=5, style="Bg.TFrame"); info.pack()
        self.level_var = tk.StringVar(value=f"Station 1: {self.stations[0]['name']}")
        ttk.Label(info, textvariable=self.level_var, font=("Arial", 14, "bold"),
                  style="Bg.TLabel").pack(side="left", padx=12)

        # 6) Spielfläche
        play = ttk.Frame(root, padding=10, style="Bg.TFrame"); play.pack(expand=True, fill="both")
        self.qvar = tk.StringVar()
        ttk.Label(play, textvariable=self.qvar, font=("Arial", 28, "bold"),
                  style="Bg.TLabel").pack(pady=(30, 15))
        self.btns = [ttk.Button(play, style="TButton") for _ in range(4)]
        for b in self.btns: b.pack(pady=8)
        self.next_btn = ttk.Button(play, text="Weiter", command=self.after_wrong)

        # 7) Mini-Karte
        self.map_canvas = tk.Canvas(root, width=MAP_W, height=MAP_H, highlightthickness=1, bd=1)
        self.map_canvas.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.map_tk = ImageTk.PhotoImage(Image.open(MAP_FILE).resize((MAP_W, MAP_H), Image.LANCZOS), master=root)
        self.map_canvas.create_image(0, 0, anchor="nw", image=self.map_tk)
        self.train_tk = ImageTk.PhotoImage(Image.open(TRAIN_ICON).convert("RGBA")
                                           .resize((24, 24), Image.LANCZOS), master=root)
        x0, y0 = self.geo_to_pixel(**self.stations[0])
        self.marker = self.map_canvas.create_image(x0, y0, anchor="center", image=self.train_tk)

        # 8) Poster + erste Frage
        self.load_poster(self.level)
        self.next_question()

    # ---------- Hilfsfunktionen ---------
    @staticmethod
    def geo_to_pixel(lat: float, lon: float, **_):
        x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * MAP_W
        y = (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * MAP_H
        return int(x), int(y)

    def load_poster(self, lvl: int):
        def poster_path(n): return BASE_PATH / f"{n}.jpg"
        while lvl > 0 and not poster_path(lvl).exists():
            lvl -= 1
        if lvl == 0:
            messagebox.showerror("Poster fehlt", "Keine Posterdatei gefunden.")
            self.root.quit(); return
        img = Image.open(poster_path(lvl)).resize((BANNER_W, BANNER_H), Image.LANCZOS)
        self.poster_tk = ImageTk.PhotoImage(img, master=self.root)
        self.canvas.itemconfig(self.poster_item, image=self.poster_tk)
        self.canvas.tag_lower(self.poster_item, self.curtain_item)

    def update_curtain(self):
        crop = self.curtain_full.crop((0, self.curtain_offset, BANNER_W, BANNER_H))
        self.curtain_img = ImageTk.PhotoImage(crop, master=self.root)
        self.canvas.itemconfig(self.curtain_item, image=self.curtain_img)

    def pull_curtain(self):
        self.curtain_offset = min(self.curtain_offset + BANNER_H // STREAK_GOAL, BANNER_H)
        self.update_curtain()

    def reset_curtain(self):
        self.curtain_offset = 0; self.update_curtain()

    # ---------- Fragenlogik -----------
    def next_question(self):
        for b in self.btns:
            b.state(["!disabled"]); b.configure(style="TButton")
        self.next_btn.pack_forget()

        de, en = random.choice(self.vocab)
        self.de, self.en = de, en
        opts = [en] + random.sample([x for _, x in self.vocab if x != en], 3)
        random.shuffle(opts)
        self.qvar.set(de)
        for btn, txt in zip(self.btns, opts):
            btn.configure(text=txt, command=lambda t=txt, b=btn: self.evaluate(t, b))

    def evaluate(self, ans, btn):
        stat = self.stats[self.de]
        if ans == self.en:                 # richtig
            self.streak += 1; self.pull_curtain()
            stat.i = min((0 if stat.n == 0 else (1 if stat.n == 1 else stat.i + 1)),
                         len(SPACING_MIN)-1)
            stat.n += 1
            stat.due = dt.datetime.now() + dt.timedelta(minutes=SPACING_MIN[stat.i])
            if self.streak == STREAK_GOAL: self.level_up()
            else:                          self.next_question()
        else:                              # falsch
            for b in self.btns:
                txt = b.cget("text")
                if txt == self.en: b.configure(style="Success.TButton")
                elif b is btn:     b.configure(style="Danger.TButton")
                b.state(["disabled"])
            self.streak = 0; self.reset_curtain()
            stat.n = stat.i = 0
            stat.due = dt.datetime.now() + dt.timedelta(minutes=SPACING_MIN[0])
            self.next_btn.pack(pady=20)

    def after_wrong(self): self.next_question()

    # ---------- Levelwechsel ----------
    def level_up(self):
        old = self.level - 1
        self.level += 1
        if self.level > self.total_levels:
            messagebox.showinfo("Ende", "Alle Stationen geschafft!"); self.root.quit(); return

        self.vocab = self.vocab_levels[self.level-1]
        self.stats = {de: Stat() for de, _ in self.vocab}
        self.load_poster(self.level); self.reset_curtain(); self.streak = 0

        name = self.stations[self.level-1]['name']
        self.level_var.set(f"Station {self.level}: {name}")

        x0, y0 = self.geo_to_pixel(**self.stations[old])
        x1, y1 = self.geo_to_pixel(**self.stations[self.level-1])
        self.animate_marker(x0, y0, x1, y1)

        messagebox.showinfo("Station geschafft", f"Weiter nach {name}")
        self.show_overview()

    # ---------- Übersichtskarte -------
    def show_overview(self):
        win = tk.Toplevel(self.root); win.title("Stations-Übersicht"); win.resizable(False, False)
        canv = tk.Canvas(win, width=MAP_W, height=MAP_H, highlightthickness=0); canv.pack(padx=20, pady=20)
        canv.bg_img = self.map_tk; canv.create_image(0, 0, anchor="nw", image=canv.bg_img)
        for st in self.stations[:self.level-1]:
            x, y = self.geo_to_pixel(**st); canv.create_oval(x-DOT_RADIUS, y-DOT_RADIUS,
                                                             x+DOT_RADIUS, y+DOT_RADIUS,
                                                             fill="#4caf50", outline="")
        x, y = self.geo_to_pixel(**self.stations[self.level-1])
        canv.train_img = self.train_tk; canv.create_image(x, y, anchor="center", image=canv.train_img)
        ttk.Button(win, text="Weiter",
                   command=lambda: (win.destroy(), self.next_question())).pack(pady=(0, 15))
        win.grab_set(); self.root.wait_window(win)

    # ---------- Animation -------------
    def animate_marker(self, x0, y0, x1, y1, steps=20):
        dx, dy = (x1-x0)/steps, (y1-y0)/steps
        def step(i, x, y):
            if i > steps: return
            self.map_canvas.coords(self.marker, x, y)
            self.root.after(15, lambda: step(i+1, x+dx, y+dy))
        step(1, x0, y0)

# -------------------- Start ------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("Bg.TFrame", background="#eef4fb")
    style.configure("Bg.TLabel", background="#eef4fb")
    style.configure("TButton",   font=("Arial", 16), padding=6)
    style.configure("Success.TButton", background="#58d068", font=("Arial", 16), padding=6)
    style.configure("Danger.TButton",  background="#e05757", font=("Arial", 16), padding=6)

    Spiel(root)
    root.mainloop()
