# poster_loader.py

from PIL import Image, ImageTk

def load_poster_image(path, size):
    """
    Lädt das Bild von `path` und skaliert es auf `size`.
    Gibt ein PhotoImage zurück.
    """
    img = Image.open(path).resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

def display_poster(game, photo_image):
    """
    Zeigt das gegebene PhotoImage im Banner-Canvas von `game`.
    Überschreibt das bisherige Bild.
    """
    game.canvas.itemconfig(game.poster_item, image=photo_image)
    game.canvas.image = photo_image  # Referenz behalten, sonst wird es garbage-collected
