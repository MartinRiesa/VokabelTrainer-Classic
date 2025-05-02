# levelwechsel.py

import fragenlogik
import level_manager
import overview_controller

def level_up(game):
    """
    Fassade: Zeigt erst die Übersichtskarte an, dann advance_level, anschließend startet die nächste Frage.
    """
    # 1) Übersichtskarte anzeigen
    overview_controller.show_overview(game)

    # 2) Level tatsächlich erhöhen
    success = level_manager.advance_level(game)
    if not success:
        return

    # 3) Quiz der neuen Stufe starten
    fragenlogik.next_question(game)
