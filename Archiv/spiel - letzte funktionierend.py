#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vokabellernspiel mit Deutschland-Reise und echter Vokabelliste.

• Stationsdaten aus leveltabelle.xlsx (Sp. C = Lat,Lon, Sp. D = Ort)
• Vokabeln aus englisch.xlsx (Sp. A = Deutsch, Sp. B = Englisch)
• 7 Vokabeln pro Station, so lange Vokabeln da sind
• Zu wenige Vokabeln → restliche Stationen werden weggelassen
• Karte unten rechts mit animiertem Zug-Icon
• Poster + Vorhang + Multiple-Choice wie gehabt
"""

import os, random, datetime as dt, tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pandas as pd

# ---------------------- Konfiguration -------------------------
EXCEL_STATIONS = "leveltabelle.xlsx"
EXCEL_VOCAB    = "englisch.xlsx"
MAP_FILE       = "germany_map.png"
TRAIN_ICON     = "train.png"
CURTAIN_FILE   = "Vorhang.png"
POSTER_PATTERN = "{}.jpg"         # 1.jpg,2.jpg,...
BANNER_W,BANNER_H = 960,360
MAP_W,MAP_H       = 200,200
STREAK_GOAL       = 10
SPACING_MIN       = (1,10,60,720,1440,4320)

# Deutschland-Grenzen für Projektion
LAT_MIN,LAT_MAX = 47.3, 55.1
LON_MIN,LON_MAX = 5.9,  15.2

# ---------------------- Statistik pro Wort ---------------------
class Stat:
    def __init__(self):
        self.EF, self.n, self.i = 2.5, 0, 1
        self.due = dt.datetime.now()
        self.wrong = []

# ---------------------- Hauptklasse Spiel ----------------------
class Spiel:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Vokabellernspiel – Deutschlandreise")
        root.geometry("1024x860")
        root.configure(bg="#eef4fb")

        # 1) Stationen einlesen
        df_st = pd.read_excel(EXCEL_STATIONS, header=None)
        coords = df_st.iloc[1:,2].astype(str).tolist()
        names  = df_st.iloc[1:,3].astype(str).tolist()
        stations = []
        for latlon,name in zip(coords,names):
            try:
                lat,lon = map(float, latlon.split(","))
                stations.append({"name":name,"lat":lat,"lon":lon})
            except:
                continue
        if not stations:
            messagebox.showerror("Fehler","Keine Stationen in Excel gefunden.")
            root.quit(); return

        # 2) Vokabelliste einlesen und in 7er‐Blöcke aufteilen
        df_v = pd.read_excel(EXCEL_VOCAB, usecols=[0,1], header=None)
        df_v.columns = ["de","en"]
        rows = list(zip(df_v["de"].astype(str), df_v["en"].astype(str)))
        n_blocks = len(rows) // 7

        # nur so viele Stationen, wie es volle 7er-Blöcke gibt
        self.total_levels = min(len(stations), n_blocks)
        if self.total_levels < len(stations):
            messagebox.showinfo(
                "Hinweis",
                f"Nur {self.total_levels} Stationen möglich, "
                "weil nicht genug Vokabeln da sind."
            )
        self.stations = stations[:self.total_levels]

        # die tatsächlichen Vokabel-Blöcke
        self.vocab_levels = [
            rows[i*7:(i+1)*7]
            for i in range(self.total_levels)
        ]

        # Startlevel
        self.level = 1
        self.vocab = self.vocab_levels[0]

        # 3) Banner (Poster + Vorhang)
        banner_fr = tk.Frame(root,bg="#eef4fb"); banner_fr.pack(pady=10)
        self.canvas = tk.Canvas(banner_fr,width=BANNER_W,height=BANNER_H,
                                highlightthickness=0)
        self.canvas.pack()
        self.poster_item = self.canvas.create_image(0,0,anchor="nw")
        self.curtain_full = Image.open(CURTAIN_FILE).convert("RGBA") \
                              .resize((BANNER_W,BANNER_H),Image.LANCZOS)
        self.curtain_img  = ImageTk.PhotoImage(self.curtain_full)
        self.curtain_item = self.canvas.create_image(0,0,anchor="nw",
                                                     image=self.curtain_img)
        self.curtain_offset = 0

        # 4) Infozeile
        info = tk.Frame(root,bg="#eef4fb"); info.pack(pady=5)
        first_name = self.stations[0]["name"]
        self.level_var = tk.StringVar(
            value=f"Station 1: {first_name}"
        )
        ttk.Label(info, textvariable=self.level_var,
                  font=("Arial",14,"bold")).pack(side="left",padx=12)
        self.opt_free = tk.BooleanVar(); self.opt_rev = tk.BooleanVar()
        ttk.Checkbutton(info,text="Freitexteingabe",
                        variable=self.opt_free).pack(side="left")
        ttk.Checkbutton(info,text="Reverse (EN→DE)",
                        variable=self.opt_rev).pack(side="left")

        # 5) Spielfläche
        play = tk.Frame(root,bg="#eef4fb"); play.pack(expand=True,fill="both")
        self.qvar = tk.StringVar()
        ttk.Label(play,textvariable=self.qvar,
                  font=("Arial",28,"bold"),
                  background="#eef4fb").pack(pady=(30,15))
        self.btns = [tk.Button(play,font=("Arial",16),width=26)
                     for _ in range(4)]
        for b in self.btns: b.pack(pady=8)
        self.next_btn=ttk.Button(play,text="Weiter",
                                 command=self.after_wrong)

        # 6) Karte + Marker
        self.map_canvas = tk.Canvas(root,width=MAP_W,height=MAP_H,
                                    highlightthickness=1,bd=1)
        self.map_canvas.place(relx=1.0,rely=1.0,anchor="se",x=-10,y=-10)
        map_img = Image.open(MAP_FILE).resize((MAP_W,MAP_H),Image.LANCZOS)
        self.map_tk = ImageTk.PhotoImage(map_img)
        self.map_canvas.create_image(0,0,anchor="nw",image=self.map_tk)
        train_img = Image.open(TRAIN_ICON).convert("RGBA") \
                         .resize((24,24),Image.LANCZOS)
        self.train_tk = ImageTk.PhotoImage(train_img)
        x0,y0 = self.geo_to_pixel(**self.stations[0])
        self.marker = self.map_canvas.create_image(x0,y0,anchor="center",
                                                   image=self.train_tk)

        # 7) Lernstatus init
        self.stats  = {de:Stat() for de,_ in self.vocab}
        self.streak = 0

        # Poster laden + Startfrage
        self.load_poster(self.level)
        self.next_question()

    # Geo → Pixel
    def geo_to_pixel(self, lat, lon, **kw):
        x = (lon - LON_MIN)/(LON_MAX-LON_MIN)*MAP_W
        y = (LAT_MAX - lat)/(LAT_MAX-LAT_MIN)*MAP_H
        return int(x), int(y)

    # Poster unter Vorhang
    def load_poster(self, lvl:int):
        while lvl>0 and not os.path.exists(POSTER_PATTERN.format(lvl)):
            lvl-=1
        if lvl==0:
            messagebox.showerror("Poster fehlt","Keine Posterdatei gefunden.")
            self.root.quit(); return
        img = Image.open(POSTER_PATTERN.format(lvl)) \
                   .resize((BANNER_W,BANNER_H),Image.LANCZOS)
        self.poster_tk = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.poster_item, image=self.poster_tk)
        self.canvas.tag_lower(self.poster_item, self.curtain_item)

    # Vorhang
    def update_curtain(self):
        crop = self.curtain_full.crop((0,self.curtain_offset,
                                       BANNER_W,BANNER_H))
        self.curtain_img = ImageTk.PhotoImage(crop)
        self.canvas.itemconfig(self.curtain_item, image=self.curtain_img)
    def pull_curtain(self):
        self.curtain_offset = min(
            self.curtain_offset + BANNER_H//STREAK_GOAL, BANNER_H
        ); self.update_curtain()
    def reset_curtain(self):
        self.curtain_offset = 0; self.update_curtain()

    # Fragenlogik
    def next_question(self):
        for b in self.btns:
            b.config(state="normal", bg="SystemButtonFace")
        self.next_btn.pack_forget()

        de,en = random.choice(self.vocab)
        self.de,self.en = de,en
        opts = [en] + random.sample([x for _,x in self.vocab if x!=en],3)
        random.shuffle(opts)
        self.qvar.set(de)
        for btn,txt in zip(self.btns,opts):
            btn.config(text=txt, command=lambda t=txt,b=btn: self.evaluate(t,b))

    # Auswertung
    def evaluate(self, ans, btn):
        stat = self.stats[self.de]
        if ans==self.en:
            self.streak+=1; self.pull_curtain()
            stat.i = 1 if stat.n==0 else (2 if stat.n==1 else stat.i+1)
            stat.n+=1
            stat.due=dt.datetime.now()+dt.timedelta(
                minutes=SPACING_MIN[stat.i])
            if self.streak==STREAK_GOAL:
                self.level_up()
            else:
                self.next_question()
        else:
            for b in self.btns:
                if b["text"]==self.en: b.config(bg="#58d068")
                elif b is btn:         b.config(bg="#e05757")
                b.config(state="disabled")
            self.streak=0; self.reset_curtain()
            stat.n=stat.i=0
            stat.due=dt.datetime.now()+dt.timedelta(
                minutes=SPACING_MIN[0])
            self.next_btn.pack(pady=20)

    def after_wrong(self):
        self.next_question()

    # Levelwechsel + Marker-Animation
    def level_up(self):
        old = self.level-1
        self.level+=1
        if self.level>self.total_levels:
            messagebox.showinfo("Ende","Alle Stationen geschafft!")
            self.root.quit(); return

        self.vocab = self.vocab_levels[self.level-1]
        self.stats = {de:Stat() for de,_ in self.vocab}
        self.load_poster(self.level)
        self.reset_curtain()
        self.streak = 0

        name = self.stations[self.level-1]["name"]
        self.level_var.set(f"Station {self.level}: {name}")

        lat0,lon0 = self.stations[old]["lat"], self.stations[old]["lon"]
        lat1,lon1 = self.stations[self.level-1]["lat"], self.stations[self.level-1]["lon"]
        x0,y0 = self.geo_to_pixel(lat0,lon0)
        x1,y1 = self.geo_to_pixel(lat1,lon1)
        self.animate_marker(x0,y0,x1,y1,steps=20)

        messagebox.showinfo("Station geschafft",f"Weiter nach {name}")
        self.next_question()

    def animate_marker(self, x0,y0,x1,y1, steps=20):
        dx,dy = (x1-x0)/steps, (y1-y0)/steps
        def step(i, x, y):
            if i>steps: return
            self.map_canvas.coords(self.marker, x, y)
            self.root.after(15, lambda: step(i+1, x+dx, y+dy))
        step(1, x0, y0)

# -------------------- Programmstart ----------------------------------------
if __name__=="__main__":
    root = tk.Tk()
    Spiel(root)
    root.mainloop()
