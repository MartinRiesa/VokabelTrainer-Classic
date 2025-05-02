# poster_effects.py

from PIL import ImageFilter

def blur_image(pil_image, radius=10):
    """
    Gibt eine verwischte Version von `pil_image` zurück.
    """
    return pil_image.filter(ImageFilter.GaussianBlur(radius))

def sharpen_image(pil_image, radius=2, percent=150, threshold=3):
    """
    Gibt eine geschärfte Version von `pil_image` zurück.
    """
    return pil_image.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))
