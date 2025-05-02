#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# main.py - Hauptstartdatei des Spiels
"""
Vokabellernspiel „Deutschland-Reise“
– mit vollflächiger Zwischenkarte, zentriertem Weiter-Button
  und garantiert unterschiedlicher Vokabelfolge
  (Fehler „unexpected keyword argument 'name'“ behoben)
"""

import tkinter as tk
from tkinter import ttk
from spiel import Spiel

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("Bg.TFrame", background="#eef4fb")
    style.configure("Bg.TLabel", background="#eef4fb")
    style.configure("TButton", font=("Arial", 16), padding=6)
    style.configure("Success.TButton", background="#58d068", font=("Arial", 16), padding=6)
    style.configure("Danger.TButton", background="#e05757", font=("Arial", 16), padding=6)

    Spiel(root)
    root.mainloop()
