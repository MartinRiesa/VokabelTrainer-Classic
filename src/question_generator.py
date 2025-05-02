# question_generator.py

import random

def pick_next_question(vocab_pool, last_question):
    """
    Wählt aus dem aktuellen Vokabel-Pool ein neues Fragepaar aus,
    das nicht der zuletzt gestellten Frage entspricht.
    Gibt das Tupel (frage, antwort) zurück.
    """
    choices = [pair for pair in vocab_pool if pair[0] != last_question]
    if not choices:
        choices = list(vocab_pool)
    q, a = random.choice(choices)
    return q, a

def build_options(vocab_pool, correct_answer, wrong_choices):
    """
    Erzeugt eine Liste von vier Antwortoptionen:
    - Erst vorhandene falsche Distraktoren (wrong_choices)
    - Dann neue Distraktoren aus dem Pool
    - Abschließend die richtige Antwort
    Mischreihenfolge wird zurückgegeben.
    """
    opts = list(wrong_choices)
    distractors = [ans for _, ans in vocab_pool if ans != correct_answer and ans not in opts]
    random.shuffle(distractors)
    opts += distractors[: max(0, 3 - len(opts))]
    opts.append(correct_answer)
    random.shuffle(opts)
    return opts
