# ui_utils.py

import tkinter as tk
from tkinter import ttk

def center_window(window):
    """
    Zentriert ein tkinter-Fenster auf dem Bildschirm.
    """
    window.update_idletasks()
    w = window.winfo_width()
    h = window.winfo_height()
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    window.geometry(f"{w}x{h}+{x}+{y}")

def create_modal_window(parent, title):
    """
    Erstellt ein modales Toplevel-Fenster mit Titel `title`, 
    blockiert Eingabe im Parent, und zentriert es.
    Gibt das neue Fenster zurück.
    """
    win = tk.Toplevel(parent)
    win.title(title)
    win.transient(parent)
    win.grab_set()
    # Styles anpassen, falls nötig
    center_window(win)
    return win

def configure_button_styles():
    """
    Definiert wiederverwendbare Button-Styles (z.B. für Success/Danger).
    Muss einmal beim GUI-Start aufgerufen werden.
    """
    style = ttk.Style()
    style.theme_use('default')
    style.configure('Success.TButton', background='green', foreground='white')
    style.map('Success.TButton',
        background=[('!disabled', 'green')],
        foreground=[('!disabled', 'white')]
    )
    style.configure('Danger.TButton', background='red', foreground='white')
    style.map('Danger.TButton',
        background=[('!disabled', 'red')],
        foreground=[('!disabled', 'white')]
    )
