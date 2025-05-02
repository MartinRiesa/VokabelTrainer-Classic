# poster.py

from config import BANNER_W, BANNER_H
from poster_loader import load_poster_image, display_poster
from poster_effects import blur_image, sharpen_image
from PIL import Image, ImageTk
import os

# Maximale Blur-Stärke (ganz verschwommen)
BLUR_MAX_RADIUS = 15

def load_poster(game, level):
    """
    Lädt und zeigt das Poster für das gegebene Level.
    Anschließend wendet es sofort den maximalen Blur an.
    """
    base_dir = os.path.dirname(__file__)
    poster_jpg = os.path.join(base_dir, f"{level}.jpg")

    if os.path.isfile(poster_jpg):
        try:
            photo = load_poster_image(poster_jpg, (BANNER_W, BANNER_H))
            display_poster(game, photo)
        except Exception:
            _draw_placeholder(game, level)
    else:
        _draw_placeholder(game, level)

    # Direkt nach Laden maximal verschwommen anzeigen
    update_blur(game, radius=BLUR_MAX_RADIUS)

def _draw_placeholder(game, level):
    game.canvas.delete("all")
    game.canvas.configure(bg="#ccc")
    game.canvas.create_text(
        BANNER_W // 2, BANNER_H // 2,
        text=f"Kein Poster für Level {level}",
        font=("Arial", 24), fill="#666"
    )
    game.poster_item = game.canvas.create_image(0, 0, anchor="nw")

def update_blur(game, radius=None):
    """
    Wendet Blur aufs aktuelle Poster an. Der Radius wird automatisch
    berechnet, wenn None, basierend auf game.streak und Levelgröße.
    """
    base_dir = os.path.dirname(__file__)
    poster_jpg = os.path.join(base_dir, f"{game.level}.jpg")
    if not os.path.isfile(poster_jpg):
        return

    # Automatische Radius-Berechnung
    if radius is None:
        total = len(game.vocab_levels[game.level - 1])
        remaining = max(total - game.streak, 0)
        ratio = remaining / total
        radius = int(BLUR_MAX_RADIUS * ratio)

    try:
        from PIL import Image
        pil_img = Image.open(poster_jpg).resize((BANNER_W, BANNER_H), Image.LANCZOS)
        blurred = blur_image(pil_img, radius)
        blurred_photo = ImageTk.PhotoImage(blurred)
        display_poster(game, blurred_photo)
    except Exception:
        pass

def update_sharpen(game):
    """
    Schärft das gesamte Poster (Radius=0).
    """
    base_dir = os.path.dirname(__file__)
    poster_jpg = os.path.join(base_dir, f"{game.level}.jpg")
    if not os.path.isfile(poster_jpg):
        return

    try:
        from PIL import Image
        pil_img = Image.open(poster_jpg).resize((BANNER_W, BANNER_H), Image.LANCZOS)
        sharp = sharpen_image(pil_img)
        sharp_photo = ImageTk.PhotoImage(sharp)
        display_poster(game, sharp_photo)
    except Exception:
        pass
