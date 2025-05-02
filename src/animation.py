"""
animation.py – Animationsfunktionen für bewegliche Elemente (z.B. das Zug-Icon auf der Karte).
"""

def animate_marker(game, x0: int, y0: int, x1: int, y1: int, steps: int = 20):
    """
    Bewegt ein Marker-Icon (z.B. den Zug auf der Karte) in einer Animation von Start- zu Zielkoordinate.
    """
    dx = (x1 - x0) / steps
    dy = (y1 - y0) / steps

    def step(i: int, x: float, y: float):
        if i > steps:
            return
        game.map_canvas.coords(game.marker, x, y)
        game.root.after(15, lambda: step(i + 1, x + dx, y + dy))

    # Animation starten
    step(1, x0, y0)
