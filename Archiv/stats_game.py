# stat.py - Enthält die Definition der Klasse Stat
import datetime as dt


class Stat:
    def __init__(self):
        self.EF, self.n, self.i = 2.5, 0, 1
        self.due = dt.datetime.now()
