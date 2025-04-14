from src.models.Card import Card, CARDS


def parse_cards(cards: str) -> list[str]:
    return [cards[i:i + 2] for i in range(0, len(cards), 2)]
