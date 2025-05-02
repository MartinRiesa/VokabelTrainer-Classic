# poster.py (aktualisiert)
from config import BANNER_W, BANNER_H
from poster_loader import load_poster_image, display_poster
from poster_effects import blur_image, sharpen_image
from station_description import StationDescription
import textwrap
from PIL import Image, ImageTk
import os

BLUR_MAX_RADIUS = 15
station_desc = StationDescription(language='de')

def load_poster(game, level):
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
    base_dir = os.path.dirname(__file__)
    poster_jpg = os.path.join(base_dir, f"{game.level}.jpg")
    if not os.path.isfile(poster_jpg):
        return
    if radius is None:
        total = len(game.vocab_levels[game.level - 1])
        remaining = max(total - game.streak, 0)
        ratio = remaining / total
        radius = int(BLUR_MAX_RADIUS * ratio)
    try:
        pil_img = Image.open(poster_jpg).resize((BANNER_W, BANNER_H), Image.LANCZOS)
        blurred = blur_image(pil_img, radius)
        blurred_photo = ImageTk.PhotoImage(blurred)
        display_poster(game, blurred_photo)
    except Exception:
        pass

def update_sharpen(game):
    base_dir = os.path.dirname(__file__)
    poster_jpg = os.path.join(base_dir, f"{game.level}.jpg")
    if not os.path.isfile(poster_jpg):
        return
    try:
        pil_img = Image.open(poster_jpg).resize((BANNER_W, BANNER_H), Image.LANCZOS)
        sharp = sharpen_image(pil_img)
        sharp_photo = ImageTk.PhotoImage(sharp)
        display_poster(game, sharp_photo)
        # Erklärungstext unter dem Bild anzeigen
        game.canvas.delete('desc_text')
        text = station_desc.get(str(game.level))
        if text:
            lines = textwrap.wrap(text, width=60)
            y_start = BANNER_H + 10
            for i, line in enumerate(lines):
                game.canvas.create_text(
                    BANNER_W // 2,
                    y_start + i * 18,
                    text=line,
                    font=("Arial", 14),
                    fill="black",
                    tags='desc_text'
                )
    except Exception:
        pass
