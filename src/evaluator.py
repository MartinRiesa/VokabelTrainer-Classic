# evaluator.py

import datetime as dt
import poster
from config import SPACING_MIN
import levelwechsel

def evaluate_answer(game, selected_answer, button):
    """
    Bewertet eine Nutzer-Auswahl: aktualisiert Leitner, passt Blur an,
    löst Level-Up aus oder fragt nächste Vokabel.
    """
    stat = game.stats[game.current_question]
    now = dt.datetime.now()

    if selected_answer == game.correct_answer:
        # Richtige Antwort
        game.streak += 1

        # Leitner-System aktualisieren
        stat.i = min(
            (0 if stat.n == 0 else (1 if stat.n == 1 else stat.i + 1)),
            len(SPACING_MIN) - 1
        )
        stat.n += 1
        stat.due = now + dt.timedelta(minutes=SPACING_MIN[stat.i])
        stat.wrong_choices.clear()

        # Wenn Level noch nicht vollendet, Blur anpassen und nächste Frage
        total = len(game.vocab_levels[game.level - 1])
        if game.streak < total:
            poster.update_blur(game)
            from quiz_flow import next_question
            next_question(game)
        else:
            # Levelende erreicht → perfekt scharf anzeigen und Level-Up
            poster.update_sharpen(game)
            levelwechsel.level_up(game)

    else:
        # Falsche Antwort markieren
        for b in game.btns:
            txt = b.cget("text")
            if txt == game.correct_answer:
                b.configure(style="Success.TButton")
            elif b is button:
                b.configure(style="Danger.TButton")
            b.state(["disabled"])

        # Reset Streak & Leitner
        game.streak = 0
        stat.n = 0
        stat.i = 0
        stat.due = now + dt.timedelta(minutes=SPACING_MIN[0])
        stat.wrong_choices = [selected_answer]

        poster.update_blur(game)

        # Weiter-Button anzeigen
        game.next_btn.config(command=lambda: __show_next(game))
        game.next_btn.pack(pady=10)

def __show_next(game):
    from quiz_flow import next_question
    game.next_btn.pack_forget()
    next_question(game)
