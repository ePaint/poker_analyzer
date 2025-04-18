from dataclasses import dataclass
from typing import Any
from src.models.InputColumn import InputColumn
from enum import StrEnum


class KPIOperation(StrEnum):
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUALS = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUALS = "lte"
    INCLUDES = "in"
    NOT_INCLUDES = "ni"


BEST_HANDS = {
    InputColumn.IS_STRAIGHT_FLUSH: "Straight Flush",
    InputColumn.IS_QUADS: "Four of a Kind",
    InputColumn.IS_FULL_HOUSE: "Full House",
    InputColumn.IS_FLUSH: "Flush",
    InputColumn.IS_STRAIGHT: "Straight",
    InputColumn.IS_TRIPS: "Three of a Kind",
    InputColumn.IS_TWO_PAIR: "Two Pair",
    InputColumn.IS_PAIR: "One Pair",
}


@dataclass
class KPIRequirement:
    column: InputColumn
    operation: KPIOperation
    value: Any

    def __str__(self):
        return f"column {self.column.value} {self.operation.value} {self.value}"

    @property
    def best_hand(self):
        return BEST_HANDS.get(self.column, "High Card")


@dataclass
class KPI:
    display_name: str
    requirements: list[KPIRequirement]
