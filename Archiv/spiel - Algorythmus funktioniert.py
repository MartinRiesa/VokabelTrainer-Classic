#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vokabel-Lernspiel – feste 10er-Serie, farbige Rückmeldung bei Fehlern
"""

import random, time, datetime as dt
import tkinter as tk
from tkinter import ttk, messagebox

# ───────────────────────── Grunddaten ──────────────────────────
VOCAB = [
    ("Apfel","apple","I eat an **apple** every morning."),
    ("Haus","house","Their **house** is very old."),
    ("Hund","dog","The **dog** is barking loudly."),
    ("Katze","cat","A **cat** sleeps most of the day."),
    ("Stuhl","chair","Please take a **chair**."),
    ("Buch","book","She is reading a good **book**."),
    ("Baum","tree","The **tree** is tall and green."),
    ("Wasser","water","Drink a glass of **water**."),
    ("Tisch","table","Lunch is on the **table**."),
    ("Auto","car","My **car** is red."),
    ("Stadt","city","Paris is a beautiful **city**."),
    ("Freund","friend","He is my best **friend**."),
    ("Schule","school","The **school** is nearby."),
    ("Brot","bread","Fresh **bread** smells great."),
    ("Ball","ball","Kick the **ball** hard."),
    ("Sonne","sun","The **sun** is shining."),
    ("Mond","moon","The **moon** is full tonight."),
    ("Fisch","fish","We ate grilled **fish**."),
    ("Milch","milk","I prefer oat **milk**."),
    ("Straße","street","Cross the **street** carefully."),
    ("Zeit","time","What **time** is it?"),
]

SPACING_MIN  = (1,10,60,720,1440,4320)   # zeitliche Intervalle
MICRO_BREAK  = 40
RT_THRESHOLD = 3.0
STREAK_TARGET = 10                       # jetzt fest!

# ────────────────────── Statistik-Objekt ──────────────────────
class WordStat:
    def __init__(self):
        self.EF = 2.5
        self.n = 0
        self.interval = 1
        self.due = dt.datetime.now()
        self.wrong_opts: list[str] = []

# ────────────────────── Hauptklasse ───────────────────────────
class Spiel:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Vokabel-Lernspiel")
        root.geometry("480x600")
        root.resizable(False, False)
        root.configure(bg="#eef4fb")

        # TTS optional
        try:
            import pyttsx3  # type: ignore
            self.engine = pyttsx3.init()
        except ImportError:
            self.engine = None

        # Style
        sty = ttk.Style(root)
        sty.theme_use("clam")
        sty.configure("bar.Horizontal.TProgressbar", thickness=18)

        # UI-Bereiche
        self.top = tk.Frame(root,bg="#eef4fb"); self.top.pack(pady=(15,0))
        self.mid = tk.Frame(root,bg="#eef4fb"); self.mid.pack(expand=True)

        self.build_top(); self.build_question(); self.build_controls()

        # Lernstatus
        self.stats  = {de: WordStat() for de, *_ in VOCAB}
        self.streak = 0
        self.total_q= 0
        self.last_show = time.time()
        self.level  = 1
        self.level_vocab = VOCAB[:7]

        # Optionen
        self.opt_free = False
        self.opt_rev  = False

        self.next_question()

    # ───────────────────────── UI-Aufbau ──────────────────────
    def build_top(self):
        self.progress = ttk.Progressbar(self.top,length=420,
                                        maximum=STREAK_TARGET,
                                        mode="determinate",
                                        style="bar.Horizontal.TProgressbar")
        self.progress.pack()
        self.status = tk.StringVar()
        ttk.Label(self.top,textvariable=self.status,font=("Arial",11),
                  background="#eef4fb").pack()

        # Checkboxen
        self.var_free = tk.BooleanVar(); self.var_rev = tk.BooleanVar()
        frm = tk.Frame(self.top,bg="#eef4fb"); frm.pack(pady=(6,0))
        ttk.Checkbutton(frm,text="Freitexteingabe",
                        variable=self.var_free,command=self.toggle_opts
                        ).pack(side="left",padx=6)
        ttk.Checkbutton(frm,text="Reverse (EN→DE)",
                        variable=self.var_rev, command=self.toggle_opts
                        ).pack(side="left",padx=6)

    def toggle_opts(self):
        self.opt_free = self.var_free.get()
        self.opt_rev  = self.var_rev.get()

    def build_question(self):
        qf = tk.Frame(self.mid,bg="#eef4fb"); qf.pack(pady=(30,15))
        self.qvar = tk.StringVar()
        self.qlabel = ttk.Label(qf,textvariable=self.qvar,font=("Arial",22,"bold"),
                                background="#eef4fb")
        self.qlabel.pack(side="left",padx=(0,10))
        tk.Button(qf,text="🔊",width=3,command=self.speak
                  ,font=("Arial",13)).pack(side="left")

    def build_controls(self):
        # Antwort-Buttons als tk.Button (für Farbänderung)
        self.mc_btns: list[tk.Button] = []
        for _ in range(4):
            b=tk.Button(self.mid,font=("Arial",13),width=22,relief="raised")
            b.pack(fill="x",padx=80,pady=6)
            self.mc_btns.append(b)
        self.entry  = ttk.Entry(self.mid,font=("Arial",14))
        self.ok_btn = ttk.Button(self.mid,text="OK",command=self.check_entry)
        # Weiter-Button
        self.next_btn = ttk.Button(self.mid,text="Weiter",command=self.after_feedback)

    # ───────────────────────── Spielablauf ────────────────────
    def next_question(self):
        # evtl. Pause
        if self.total_q and self.total_q%MICRO_BREAK==0:
            messagebox.showinfo("Pause","Kurze Pause – weiter in 30 s.")
            self.root.after(30000,self.next_question); return

        now = dt.datetime.now()
        due = [(d,e,s) for d,e,s in self.level_vocab if self.stats[d].due<=now] or self.level_vocab
        weights = [1/(self.stats[d].interval+0.5) for d,_,_ in due]
        self.de,self.en,self.sent = random.choices(due,weights)[0]

        # Modus
        reverse = self.opt_rev and self.total_q%5==0 and self.stats[self.de].n>=1
        free    = self.opt_free and self.total_q%5==0 and self.stats[self.de].n>=1
        self.mode = ("reverse_" if reverse else "normal_")+("free" if free else "mc")

        self.show_question()
        self.last_show=time.time()
        self.total_q+=1

    def show_question(self):
        reverse = self.mode.startswith("reverse")
        free    = self.mode.endswith("free")

        self.qvar.set(self.en if reverse else self.de)
        self.qlabel.unbind("<Enter>"); self.qlabel.unbind("<Leave>")

        for b in self.mc_btns: b.pack_forget()
        self.entry.pack_forget(); self.ok_btn.pack_forget()
        self.next_btn.pack_forget()

        # Multiple-Choice
        if not free:
            opts=self.make_options(reverse)
            for b,ans in zip(self.mc_btns,opts):
                b.config(text=ans,bg="SystemButtonFace",state="normal",
                         command=lambda a=ans,bt=b: self.evaluate(a,bt))
                b.pack(fill="x",padx=80,pady=6)
        else:
            # Freitext
            self.entry.delete(0,"end")
            self.entry.pack(padx=60,pady=8,fill="x")
            self.ok_btn.pack(pady=4); self.entry.focus()

    def make_options(self,reverse: bool):
        correct = self.de if reverse else self.en
        stat    = self.stats[self.de]
        rec     = stat.wrong_opts[:2]

        pool = ([d for d,_,_ in self.level_vocab] if reverse
                else [e for _,e,_ in self.level_vocab])
        pool=[x for x in pool if x not in rec and x!=correct]
        random.shuffle(pool)
        opts=[correct]+rec+pool
        opts=opts[:4]
        while len(opts)<4:
            extra=random.choice(pool)
            if extra not in opts: opts.append(extra)
        random.shuffle(opts); return opts

    # ────────────────── Eingabe & Bewertung ───────────────────
    def check_entry(self): self.evaluate(self.entry.get().strip(),None)

    def evaluate(self, answer:str, btn_clicked: tk.Button | None):
        reverse = self.mode.startswith("reverse")
        free    = self.mode.endswith("free")
        correct_str = self.de if reverse else self.en
        correct = (answer.strip().lower()==correct_str.lower())

        stat=self.stats[self.de]

        if correct:
            self.handle_correct(stat)
            self.next_question()
        else:
            self.handle_wrong(stat, answer, btn_clicked, correct_str)

    # ────────────────── Richtig / Falsch Handlers ─────────────
    def handle_correct(self,stat):
        self.streak+=1
        if stat.n==0:   stat.interval=1
        elif stat.n==1: stat.interval=2
        else:           stat.interval=min(stat.interval+1,len(SPACING_MIN)-1)
        stat.n+=1
        stat.due=dt.datetime.now()+dt.timedelta(minutes=SPACING_MIN[stat.interval])

        self.progress["value"]=self.streak
        self.status.set(f"Level {self.level} – Serie {self.streak}/{STREAK_TARGET}")
        if self.streak==STREAK_TARGET: self.level_up()

    def handle_wrong(self,stat,answer,btn_clicked,correct_str):
        # Recycling
        if answer and answer not in stat.wrong_opts:
            stat.wrong_opts.insert(0,answer)
        stat.wrong_opts=stat.wrong_opts[:3]
        # Reset
        stat.n=0; stat.interval=0; stat.due=dt.datetime.now()+dt.timedelta(minutes=SPACING_MIN[0])
        self.streak=0
        self.progress["value"]=0
        self.status.set(f"Level {self.level} – Serie 0/{STREAK_TARGET}")

        # Visual feedback nur bei MC
        if btn_clicked:
            for b in self.mc_btns:
                if b["text"]==correct_str: b.config(bg="#58d068")   # grün
                elif b is btn_clicked:     b.config(bg="#e05757")   # rot
                b.config(state="disabled")
            self.next_btn.pack(pady=10)
        else:
            # Freitext: simple Meldung
            messagebox.showwarning("Falsch",f"Richtig wäre: {correct_str}")
            self.next_question()

    def after_feedback(self):
        self.next_btn.pack_forget()
        self.next_question()

    # ────────────────── Level-Wechsel ────────────────────────
    def level_up(self):
        if self.level==3:
            messagebox.showinfo("Geschafft","🎉 Alle Level beendet!")
            self.root.quit(); return
        self.level+=1; self.level_vocab=VOCAB[:7*self.level]
        self.streak=0; self.progress["value"]=0
        messagebox.showinfo("Level up",f"Level {self.level} gestartet!")

    # ────────────────── Hilfsfunktionen ─────────────────────
    def speak(self):
        if self.engine: self.engine.say(self.de); self.engine.runAndWait()

# ───────────────────────────────────────────────────────────
if __name__=="__main__":
    root=tk.Tk(); Spiel(root); root.mainloop()
