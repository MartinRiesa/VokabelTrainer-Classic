# poster_effects.py (aktualisiert)
from PIL import ImageFilter
import pygame
import textwrap
from station_description import StationDescription

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

class PosterEffects:
    """
    Erweiterung: Zeigt nach dem Entblurren das Bild und darunter den Erklärungstext an.
    """
    def __init__(self, screen, language='de'):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.station_desc = StationDescription(language)

    def entblurren_und_anzeigen(self, image_surface, station_id):
        image_rect = image_surface.get_rect(center=(self.screen.get_width()/2,
                                                   self.screen.get_height()/2 - 50))
        self.screen.blit(image_surface, image_rect)
        text = self.station_desc.get(station_id)
        if text:
            lines = textwrap.wrap(text, width=60)
            y_offset = image_rect.bottom + 10
            for line in lines:
                text_surf = self.font.render(line, True, (0, 0, 0))
                text_rect = text_surf.get_rect(centerx=self.screen.get_width()/2, top=y_offset)
                self.screen.blit(text_surf, text_rect)
                y_offset += text_surf.get_height() + 5
        pygame.display.update()
