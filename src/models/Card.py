from dataclasses import dataclass
from enum import StrEnum, Enum


class Suit(StrEnum):
    HEARTS = "h"
    DIAMONDS = "d"
    CLUBS = "c"
    SPADES = "s"


class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


@dataclass
class Card:
    suit: Suit
    rank: Rank
    raw: str

    def __str__(self):
        return self.raw

    def __repr__(self):
        return self.raw


CARDS = {
    "Ah": Card(suit=Suit.HEARTS, rank=Rank.ACE, raw="Ah"),
    "2h": Card(suit=Suit.HEARTS, rank=Rank.TWO, raw="2h"),
    "3h": Card(suit=Suit.HEARTS, rank=Rank.THREE, raw="3h"),
    "4h": Card(suit=Suit.HEARTS, rank=Rank.FOUR, raw="4h"),
    "5h": Card(suit=Suit.HEARTS, rank=Rank.FIVE, raw="5h"),
    "6h": Card(suit=Suit.HEARTS, rank=Rank.SIX, raw="6h"),
    "7h": Card(suit=Suit.HEARTS, rank=Rank.SEVEN, raw="7h"),
    "8h": Card(suit=Suit.HEARTS, rank=Rank.EIGHT, raw="8h"),
    "9h": Card(suit=Suit.HEARTS, rank=Rank.NINE, raw="9h"),
    "Th": Card(suit=Suit.HEARTS, rank=Rank.TEN, raw="Th"),
    "Jh": Card(suit=Suit.HEARTS, rank=Rank.JACK, raw="Jh"),
    "Qh": Card(suit=Suit.HEARTS, rank=Rank.QUEEN, raw="Qh"),
    "Kh": Card(suit=Suit.HEARTS, rank=Rank.KING, raw="Kh"),
    "Ad": Card(suit=Suit.DIAMONDS, rank=Rank.ACE, raw="Ad"),
    "2d": Card(suit=Suit.DIAMONDS, rank=Rank.TWO, raw="2d"),
    "3d": Card(suit=Suit.DIAMONDS, rank=Rank.THREE, raw="3d"),
    "4d": Card(suit=Suit.DIAMONDS, rank=Rank.FOUR, raw="4d"),
    "5d": Card(suit=Suit.DIAMONDS, rank=Rank.FIVE, raw="5d"),
    "6d": Card(suit=Suit.DIAMONDS, rank=Rank.SIX, raw="6d"),
    "7d": Card(suit=Suit.DIAMONDS, rank=Rank.SEVEN, raw="7d"),
    "8d": Card(suit=Suit.DIAMONDS, rank=Rank.EIGHT, raw="8d"),
    "9d": Card(suit=Suit.DIAMONDS, rank=Rank.NINE, raw="9d"),
    "Td": Card(suit=Suit.DIAMONDS, rank=Rank.TEN, raw="Td"),
    "Jd": Card(suit=Suit.DIAMONDS, rank=Rank.JACK, raw="Jd"),
    "Qd": Card(suit=Suit.DIAMONDS, rank=Rank.QUEEN, raw="Qd"),
    "Kd": Card(suit=Suit.DIAMONDS, rank=Rank.KING, raw="Kd"),
    "Ac": Card(suit=Suit.CLUBS, rank=Rank.ACE, raw="Ac"),
    "2c": Card(suit=Suit.CLUBS, rank=Rank.TWO, raw="2c"),
    "3c": Card(suit=Suit.CLUBS, rank=Rank.THREE, raw="3c"),
    "4c": Card(suit=Suit.CLUBS, rank=Rank.FOUR, raw="4c"),
    "5c": Card(suit=Suit.CLUBS, rank=Rank.FIVE, raw="5c"),
    "6c": Card(suit=Suit.CLUBS, rank=Rank.SIX, raw="6c"),
    "7c": Card(suit=Suit.CLUBS, rank=Rank.SEVEN, raw="7c"),
    "8c": Card(suit=Suit.CLUBS, rank=Rank.EIGHT, raw="8c"),
    "9c": Card(suit=Suit.CLUBS, rank=Rank.NINE, raw="9c"),
    "Tc": Card(suit=Suit.CLUBS, rank=Rank.TEN, raw="Tc"),
    "Jc": Card(suit=Suit.CLUBS, rank=Rank.JACK, raw="Jc"),
    "Qc": Card(suit=Suit.CLUBS, rank=Rank.QUEEN, raw="Qc"),
    "Kc": Card(suit=Suit.CLUBS, rank=Rank.KING, raw="Kc"),
    "As": Card(suit=Suit.SPADES, rank=Rank.ACE, raw="As"),
    "2s": Card(suit=Suit.SPADES, rank=Rank.TWO, raw="2s"),
    "3s": Card(suit=Suit.SPADES, rank=Rank.THREE, raw="3s"),
    "4s": Card(suit=Suit.SPADES, rank=Rank.FOUR, raw="4s"),
    "5s": Card(suit=Suit.SPADES, rank=Rank.FIVE, raw="5s"),
    "6s": Card(suit=Suit.SPADES, rank=Rank.SIX, raw="6s"),
    "7s": Card(suit=Suit.SPADES, rank=Rank.SEVEN, raw="7s"),
    "8s": Card(suit=Suit.SPADES, rank=Rank.EIGHT, raw="8s"),
    "9s": Card(suit=Suit.SPADES, rank=Rank.NINE, raw="9s"),
    "Ts": Card(suit=Suit.SPADES, rank=Rank.TEN, raw="Ts"),
    "Js": Card(suit=Suit.SPADES, rank=Rank.JACK, raw="Js"),
    "Qs": Card(suit=Suit.SPADES, rank=Rank.QUEEN, raw="Qs"),
    "Ks": Card(suit=Suit.SPADES, rank=Rank.KING, raw="Ks"),
}
