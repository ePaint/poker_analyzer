from pydantic import BaseModel, Field

from src.models.Card import Card


class Entry(BaseModel):
    chance: int = 0  # value between 0 and 100000, where 0 is 0% and 100000 is 100%
    cards: list[Card] = Field(default_factory=list)
