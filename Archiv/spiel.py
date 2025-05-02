# spiel.py – Hauptklasse Spiel mit Text-to-Speech-Unterstützung
import random
import datetime as dt
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pandas as pd
import pyttsx3                       # Offline-TTS

from config import (
    BASE_PATH, EXCEL_STATIONS, EXCEL_VOCAB, MAP_FILE, TRAIN_ICON,
    CURTAIN_FILE, BANNER_W, BANNER_H, MAP_SMALL, MAP_LARGE,
    STREAK_GOAL, SPACING_MIN, DOT_RADIUS, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX
)
from stats_game import Stat


class Spiel:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Vokabellernspiel – Deutschland-Reise")
        root.geometry("1024x860")
        root.configure(bg="#eef4fb")

        # ----------------- TTS-Engine (deutsche Stimme, falls verfügbar) -------------
        self.tts = pyttsx3.init()
        for v in self.tts.getProperty("voices"):
            # Je nach Plattform: languages kann bytes[] | str sein
            langs = [l.decode() if isinstance(l, bytes) else l for l in getattr(v, "languages", [])]
            if any("de" in l.lower() for l in langs) or "german" in v.name.lower():
                self.tts.setProperty("voice", v.id)
                break

        # ----------------- 1) Stationen ---------------------------------------------
        df_st = pd.read_excel(EXCEL_STATIONS, header=None)
        self.stations = []
        for latlon, name in zip(df_st.iloc[1:, 2], df_st.iloc[1:, 3]):
            try:
                lat, lon = map(float, str(latlon).split(","))
                self.stations.append({"name": str(name), "lat": lat, "lon": lon})
            except ValueError:
                continue
        if not self.stations:
            messagebox.showerror("Fehler", "Keine Stationen gefunden.")
            root.quit()
            return

        # ----------------- 2) Vokabeln ----------------------------------------------
        df_v = pd.read_excel(EXCEL_VOCAB, usecols=[0, 1], header=None)
        rows   = list(zip(df_v[0].astype(str), df_v[1].astype(str)))
        blocks = len(rows) // 7
        self.total_levels = min(len(self.stations), blocks)
        self.stations     = self.stations[:self.total_levels]
        self.vocab_levels = [rows[i*7:(i+1)*7] for i in range(self.total_levels)]

        # ----------------- 3) Startzustand ------------------------------------------
        self.level    = 1
        self.vocab    = self.vocab_levels[0]
        self.stats    = {de: Stat() for de, _ in self.vocab}
        self.streak   = 0
        self.last_de  = None                     # zuletzt gestellte deutsche Vokabel

        # ----------------- 4) Banner ------------------------------------------------
        banner_fr = ttk.Frame(root, padding=10, style="Bg.TFrame")
        banner_fr.pack()
        self.canvas = tk.Canvas(banner_fr, width=BANNER_W, height=BANNER_H,
                                highlightthickness=0)
        self.canvas.pack()
        self.poster_item = self.canvas.create_image(0, 0, anchor="nw")
        self.curtain_full = Image.open(CURTAIN_FILE).convert("RGBA").resize(
            (BANNER_W, BANNER_H), Image.LANCZOS
        )
        self.curtain_img  = ImageTk.PhotoImage(self.curtain_full, master=root)
        self.curtain_item = self.canvas.create_image(0, 0, anchor="nw",
                                                     image=self.curtain_img)
        self.curtain_offset = 0

        # ----------------- 5) Infozeile --------------------------------------------
        info = ttk.Frame(root, padding=5, style="Bg.TFrame")
        info.pack()
        self.level_var = tk.StringVar(value=f"Station 1: {self.stations[0]['name']}")
        ttk.Label(info, textvariable=self.level_var, font=("Arial", 14, "bold"),
                  style="Bg.TLabel").pack(side="left", padx=12)

        # ----------------- 6) Spielfläche ------------------------------------------
        play = ttk.Frame(root, padding=10, style="Bg.TFrame")
        play.pack(expand=True, fill="both")

        # Fragebereich (Label + Lautsprecherbutton nebeneinander)
        self.qvar = tk.StringVar()
        qrow = ttk.Frame(play, style="Bg.TFrame")
        qrow.pack(pady=(30, 15))

        ttk.Label(qrow, textvariable=self.qvar, font=("Arial", 28, "bold"),
                  style="Bg.TLabel").pack(side="left")

        self.speaker_btn = ttk.Button(qrow, text="🔊", width=3,
                                      command=self.speak_current_word)
        self.speaker_btn.pack(side="left", padx=10)

        self.btns = [ttk.Button(play, style="TButton") for _ in range(4)]
        for b in self.btns:
            b.pack(pady=8)
        self.next_btn = ttk.Button(play, text="Weiter", command=self.after_wrong)

        # ----------------- 7) Mini-Karte -------------------------------------------
        w_small, h_small = MAP_SMALL
        self.map_canvas = tk.Canvas(root, width=w_small, height=h_small,
                                    highlightthickness=1, bd=1)
        self.map_canvas.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.map_tk = ImageTk.PhotoImage(
            Image.open(MAP_FILE).resize(MAP_SMALL, Image.LANCZOS),
            master=root
        )
        self.map_canvas.create_image(0, 0, anchor="nw", image=self.map_tk)
        self.train_tk = ImageTk.PhotoImage(
            Image.open(TRAIN_ICON).convert("RGBA").resize((24, 24), Image.LANCZOS),
            master=root
        )
        lat0, lon0 = self.stations[0]['lat'], self.stations[0]['lon']
        x0, y0 = self.geo_to_pixel(lat0, lon0, map_w=w_small, map_h=h_small)
        self.marker = self.map_canvas.create_image(x0, y0, anchor="center",
                                                   image=self.train_tk)

        # ----------------- 8) Poster + erste Frage ---------------------------------
        self.load_poster(self.level)
        self.next_question()

    # ======================== Hilfsfunktionen ======================================
    @staticmethod
    def geo_to_pixel(lat: float, lon: float, *, map_w: int, map_h: int):
        x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * map_w
        y = (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * map_h
        return int(x), int(y)

    # ----------------- TTS ---------------------------------------------------------
    def speak_current_word(self):
        """Spricht das aktuell angezeigte deutsche Wort."""
        if not getattr(self, "de", None):
            return
        # In eigenem Thread, damit GUI nicht blockiert
        threading.Thread(target=self._tts_say, args=(self.de,), daemon=True).start()

    def _tts_say(self, text: str):
        try:
            self.tts.say(text)
            self.tts.runAndWait()
        except RuntimeError:
            # Fallback: neues Engine-Objekt, falls parallel genutzt wurde
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()

    # ----------------- Postersteuerung --------------------------------------------
    def load_poster(self, lvl: int):
        def poster_path(n): return BASE_PATH / f"{n}.jpg"
        while lvl > 0 and not poster_path(lvl).exists():
            lvl -= 1
        if lvl == 0:
            messagebox.showerror("Poster fehlt", "Keine Posterdatei gefunden.")
            self.root.quit()
            return
        img = Image.open(poster_path(lvl)).resize((BANNER_W, BANNER_H), Image.LANCZOS)
        self.poster_tk = ImageTk.PhotoImage(img, master=self.root)
        self.canvas.itemconfig(self.poster_item, image=self.poster_tk)
        self.canvas.tag_lower(self.poster_item, self.curtain_item)

    def update_curtain(self):
        crop = self.curtain_full.crop((0, self.curtain_offset, BANNER_W, BANNER_H))
        self.curtain_img = ImageTk.PhotoImage(crop, master=self.root)
        self.canvas.itemconfig(self.curtain_item, image=self.curtain_img)

    def pull_curtain(self):
        self.curtain_offset = min(self.curtain_offset + BANNER_H // STREAK_GOAL,
                                  BANNER_H)
        self.update_curtain()

    def reset_curtain(self):
        self.curtain_offset = 0
        self.update_curtain()

    # ----------------- Fragenlogik -------------------------------------------------
    def next_question(self):
        for b in self.btns:
            b.state(["!disabled"])
            b.configure(style="TButton")
        self.next_btn.pack_forget()

        # Vokabel auswählen – nicht dieselbe wie zuletzt
        choices = [pair for pair in self.vocab if pair[0] != self.last_de]
        if not choices:
            choices = self.vocab
        de, en = random.choice(choices)
        self.last_de = de

        self.de, self.en = de, en
        opts = [en] + random.sample([x for _, x in self.vocab if x != en], 3)
        random.shuffle(opts)

        self.qvar.set(de)
        for btn, txt in zip(self.btns, opts):
            btn.configure(text=txt,
                          command=lambda t=txt, b=btn: self.evaluate(t, b))

    def evaluate(self, ans, btn):
        stat = self.stats[self.de]
        if ans == self.en:                 # richtig
            self.streak += 1
            self.pull_curtain()
            stat.i = min((0 if stat.n == 0 else
                          (1 if stat.n == 1 else stat.i + 1)),
                         len(SPACING_MIN) - 1)
            stat.n  += 1
            stat.due = dt.datetime.now() + dt.timedelta(minutes=SPACING_MIN[stat.i])
            if self.streak == STREAK_GOAL:
                self.level_up()
            else:
                self.next_question()
        else:                              # falsch
            for b in self.btns:
                txt = b.cget("text")
                if txt == self.en:
                    b.configure(style="Success.TButton")
                elif b is btn:
                    b.configure(style="Danger.TButton")
                b.state(["disabled"])
            self.streak = 0
            self.reset_curtain()
            stat.n = stat.i = 0
            stat.due = dt.datetime.now() + dt.timedelta(minutes=SPACING_MIN[0])
            self.next_btn.pack(pady=20)

    def after_wrong(self):
        self.next_question()

    # ----------------- Levelwechsel -----------------------------------------------
    def level_up(self):
        old = self.level - 1
        self.level += 1
        if self.level > self.total_levels:
            messagebox.showinfo("Ende", "Alle Stationen geschafft!")
            self.root.quit()
            return

        self.vocab  = self.vocab_levels[self.level - 1]
        self.stats  = {de: Stat() for de, _ in self.vocab}
        self.load_poster(self.level)
        self.reset_curtain()
        self.streak = 0
        self.last_de = None

        name = self.stations[self.level - 1]['name']
        self.level_var.set(f"Station {self.level}: {name}")

        # Zug-Animation auf der Minikarte
        lat_old, lon_old = self.stations[old]['lat'], self.stations[old]['lon']
        lat_new, lon_new = self.stations[self.level - 1]['lat'], self.stations[self.level - 1]['lon']
        x0, y0 = self.geo_to_pixel(lat_old, lon_old, map_w=MAP_SMALL[0],
                                   map_h=MAP_SMALL[1])
        x1, y1 = self.geo_to_pixel(lat_new, lon_new, map_w=MAP_SMALL[0],
                                   map_h=MAP_SMALL[1])
        self.animate_marker(x0, y0, x1, y1)

        messagebox.showinfo("Station geschafft", f"Weiter nach {name}")
        self.show_overview()

    # ----------------- Übersichtskarte --------------------------------------------
    def show_overview(self):
        win = tk.Toplevel(self.root)
        win.title("Stations-Übersicht")
        w_big, h_big = MAP_LARGE
        win.geometry(f"{w_big}x{h_big}")
        win.resizable(False, False)

        canv = tk.Canvas(win, width=w_big, height=h_big, highlightthickness=0)
        canv.pack()

        img_big = ImageTk.PhotoImage(
            Image.open(MAP_FILE).resize(MAP_LARGE, Image.LANCZOS),
            master=win
        )
        canv.create_image(0, 0, anchor="nw", image=img_big)
        canv.bg_img = img_big    # Referenz halten

        for st in self.stations[:self.level - 1]:
            x, y = self.geo_to_pixel(st['lat'], st['lon'],
                                     map_w=w_big, map_h=h_big)
            canv.create_oval(x - DOT_RADIUS, y - DOT_RADIUS,
                             x + DOT_RADIUS, y + DOT_RADIUS,
                             fill="#4caf50", outline="")

        lat_cur, lon_cur = self.stations[self.level - 1]['lat'], self.stations[self.level - 1]['lon']
        x, y = self.geo_to_pixel(lat_cur, lon_cur, map_w=w_big, map_h=h_big)
        canv.train_img = self.train_tk
        canv.create_image(x, y, anchor="center", image=canv.train_img)

        # zentrierter Weiter-Button
        btn = ttk.Button(win, text="Weiter",
                         command=lambda: (win.destroy(), self.next_question()))
        canv.create_window(w_big // 2, h_big // 2, window=btn)

        win.grab_set()
        self.root.wait_window(win)

    # ----------------- Animation ---------------------------------------------------
    def animate_marker(self, x0, y0, x1, y1, steps=20):
        dx, dy = (x1 - x0) / steps, (y1 - y0) / steps

        def step(i, x, y):
            if i > steps:
                return
            self.map_canvas.coords(self.marker, x, y)
            self.root.after(15, lambda: step(i + 1, x + dx, y + dy))

        step(1, x0, y0)
