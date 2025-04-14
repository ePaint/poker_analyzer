from itertools import combinations
from pathlib import Path

from src.card_parser import parse_cards
from src.models.Action import Action


class File:
    def __init__(self, file: Path):
        self.path = file
        cards_raw, action_raw = self.path.stem.split("_")
        self.cards = parse_cards(cards_raw)
        self.action = Action(action_raw.casefold())

    def __str__(self):
        return f"File(path={self.path}, cards={self.cards}, action={self.action})"

    @property
    def combos(self):
        return list(combinations(self.cards, 3))
