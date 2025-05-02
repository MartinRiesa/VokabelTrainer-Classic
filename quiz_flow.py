# quiz_flow.py

from question_generator import pick_next_question, build_options
from evaluator import evaluate_answer

def next_question(game):
    """
    Liefert die nächste Frage:
    - Buttons zurücksetzen
    - Frage und Antwort auswählen
    - Antwort-Buttons mit Optionen belegen und auswerten
    """
    # Buttons reaktivieren
    for btn in game.btns:
        btn.state(["!disabled"])
        btn.configure(style="TButton")
    # Weiter-Button verstecken
    game.next_btn.pack_forget()

    # Frage auswählen
    q, a = pick_next_question(game.vocab_pool, game.last_question)
    game.last_question       = q
    game.current_question    = q
    game.correct_answer      = a

    # Optionen zusammenstellen
    opts = build_options(game.vocab_pool, a, game.stats[q].wrong_choices)

    # Buttons belegen
    for btn, txt in zip(game.btns, opts):
        btn.config(text=txt)
        btn.config(command=lambda b=btn, t=txt: evaluate_answer(game, t, b))

    # Frage anzeigen
    game.qvar.set(q)
