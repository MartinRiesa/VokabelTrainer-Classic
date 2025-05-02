# fragenlogik.py

from quiz_flow import next_question as _next_question
from evaluator import evaluate_answer as _evaluate_answer

def next_question(game):
    """Weiterleitung an den Quiz-Flow."""
    _next_question(game)

def evaluate(game, answer, button):
    """Weiterleitung an den Evaluator."""
    _evaluate_answer(game, answer, button)

def after_wrong(game):
    """Wird aufgerufen, wenn eine falsche Antwort angezeigt wurde."""
    next_question(game)
