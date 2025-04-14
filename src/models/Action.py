from enum import StrEnum


class Action(StrEnum):
    CALL = "call"
    FOLD = "fold"
    RAISE = "raise"
    CHECK = "check"
    BET = "bet"
