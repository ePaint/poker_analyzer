from enum import StrEnum


class InputColumn(StrEnum):
    ROW_IDX = "row_idx"
    ACTION = "action"
    WEIGHT = "weight"
    COMMUNITY_CARDS = "community_cards"
    HOLE_CARDS = "hole_cards"
    IS_FLUSH = "is_flush"
    IS_STRAIGHT = "is_straight"
    IS_STRAIGHT_FLUSH = "is_straight_flush"
    IS_PAIR = "is_pair"
    IS_TWO_PAIR = "is_two_pair"
    IS_TRIPS = "is_trips"
    IS_QUADS = "is_quads"
    IS_FULL_HOUSE = "is_full_house"
    PAIR_RANK = "pair_rank"
    FULL_HOUSE_PAIR_RANK = "full_house_pair_rank"
    FLUSH_RANK = "flush_rank"
    STRAIGHT_RANK = "straight_rank"
    SET_RANK = "set_rank"
    BEST_HAND = "best_hand"
