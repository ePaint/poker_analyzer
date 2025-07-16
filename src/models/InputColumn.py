from enum import StrEnum


class InputColumn(StrEnum):
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
    BEST_HAND_VALUE = "best_hand_value"  # 1 = Straight Flush, 2 = Four of a Kind, 3 = Straight, 4 = Full House, 5 = Flush, 6 = Three of a Kind, 7 = Two Pair, 8 = One Pair, 9 = High Card
    FLUSH_DRAW = "flush_draw"
    DRAW_STRAIGHT_RANKS = "draw_straight_ranks"
    DRAW_STRAIGHT_OUTS = "draw_straight_outs"
