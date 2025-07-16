from itertools import combinations
from pathlib import Path

from src.models.Action import Action


class File:
    def __init__(self, file: Path):
        self.path = file
        cards_raw, action_raw = self.path.stem.split("_")
        self.cards = self.parse_cards(cards_raw)
        action_raw = action_raw.casefold().replace("raise", "bet")
        self.action = Action(action_raw)

    def __str__(self):
        return f"File(path={self.path}, cards={self.cards}, action={self.action})"

    @staticmethod
    def parse_cards(cards: str) -> list[str]:
        return [cards[i: i + 2] for i in range(0, len(cards), 2)]

    @property
    def combos(self):
        return list(combinations(self.cards, 3))
