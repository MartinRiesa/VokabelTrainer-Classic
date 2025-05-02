import pygame
from station_description import StationDescription
import textwrap

class PosterEffects:
    def __init__(self, screen, language='de'):
        self.screen = screen  # Pygame-Display-Surface
        self.font = pygame.font.Font(None, 24)  # Schriftart für den Text
        self.station_desc = StationDescription(language)

    def entblurren_und_anzeigen(self, image_surface, station_id):
        # Hier wird angenommen, dass image_surface bereits geladen ist,
        # und die Entblurren-Animation erfolgt vor dieser Anzeige.
        # Beispiel: ein Loop, der nach und nach die Bilddetails freigibt.
        #
        # --- (Entblurren-Logik nicht gezeigt) ---
        #
        # Am Ende des Effekts ist image_surface vollständig sichtbar:
        image_rect = image_surface.get_rect(center=(self.screen.get_width()/2,
                                                   self.screen.get_height()/2 - 50))
        # Zeichne das Bild
        self.screen.blit(image_surface, image_rect)
        
        # Nun die Stationsbeschreibung laden
        text = self.station_desc.get(station_id)
        if text:
            # Umbrüche einfügen, damit der Text nicht zu breit wird
            lines = textwrap.wrap(text, width=60)
            y_offset = image_rect.bottom + 10  # Startposition unter dem Bild
            for line in lines:
                text_surf = self.font.render(line, True, (0, 0, 0))
                # Zentriere den Text unter dem Bild
                text_rect = text_surf.get_rect(centerx=self.screen.get_width()/2, top=y_offset)
                self.screen.blit(text_surf, text_rect)
                y_offset += text_surf.get_height() + 5

        # Bildschirm aktualisieren (bei Pygame)
        pygame.display.update()
