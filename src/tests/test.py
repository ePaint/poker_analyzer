import pandas as pd

from main import hand_rank, categorize_hand
from src.models.Card import CARDS


def test_gutshot():
    # test [5h, 7h, 7s, 8c, Ts]
    """Ensure 5h7h7s8cTs is classified as a gutshot draw."""
    hand = [CARDS["5h"], CARDS["7h"], CARDS["7s"], CARDS["8c"], CARDS["Ts"]]
    result = hand_rank(hand)
    assert result["is_gutshot"], "5h7h7s8cTs should be a gutshot."


def test_no_gutshot():
    """Ensure AhAs4s3s2s is NOT classified as a gutshot draw."""
    gutshot_hands = [
        [CARDS["Ah"], CARDS["Kd"], CARDS["Jh"], CARDS["Td"], CARDS["8s"]],  # Needs Q
        [CARDS["9h"], CARDS["6d"], CARDS["7s"], CARDS["5h"], CARDS["3d"]],  # Needs 8
        [CARDS["Qh"], CARDS["9d"], CARDS["Jh"], CARDS["Ts"], CARDS["7c"]],  # Needs 8
        [CARDS["8h"], CARDS["5d"], CARDS["6s"], CARDS["4h"], CARDS["2d"]],  # Needs 7
        [CARDS["Th"], CARDS["7d"], CARDS["8s"], CARDS["6h"], CARDS["4d"]],  # Needs 9
        [CARDS["Jh"], CARDS["8d"], CARDS["9s"], CARDS["7h"], CARDS["5d"]],  # Needs 10
        [CARDS["Kh"], CARDS["Td"], CARDS["Jc"], CARDS["9h"], CARDS["7s"]],  # Needs Q
        [CARDS["Qh"], CARDS["Jd"], CARDS["9s"], CARDS["8h"], CARDS["6c"]],  # Needs 10
        [CARDS["5h"], CARDS["2d"], CARDS["3s"], CARDS["4h"], CARDS["7c"]],  # Needs 6
        [CARDS["Ah"], CARDS["Qd"], CARDS["Kc"], CARDS["Jh"], CARDS["9s"]],  # Needs 10
        [CARDS["9h"], CARDS["7d"], CARDS["8s"], CARDS["6h"], CARDS["4c"]],  # Needs 5
        [CARDS["Kh"], CARDS["Jd"], CARDS["Qh"], CARDS["9s"], CARDS["7c"]],  # Needs 10
        [CARDS["8h"], CARDS["6d"], CARDS["7s"], CARDS["5h"], CARDS["3c"]],  # Needs 4
        [CARDS["Th"], CARDS["8d"], CARDS["9s"], CARDS["7h"], CARDS["5c"]],  # Needs 6
        [CARDS["7h"], CARDS["5d"], CARDS["6s"], CARDS["4h"], CARDS["2c"]],  # Needs 3
        [CARDS["Jh"], CARDS["9d"], CARDS["Th"], CARDS["8s"], CARDS["6c"]],  # Needs 7
        [CARDS["Qh"], CARDS["Jd"], CARDS["Kh"], CARDS["9s"], CARDS["7c"]],  # Needs 10
        [CARDS["5h"], CARDS["3d"], CARDS["4s"], CARDS["2h"], CARDS["7c"]],  # Needs 6
        [CARDS["9h"], CARDS["6d"], CARDS["7s"], CARDS["5h"], CARDS["3c"]],  # Needs 8
        [CARDS["Ah"], CARDS["Jd"], CARDS["Qh"], CARDS["Th"], CARDS["8s"]],  # Needs K
    ]
    for hand in gutshot_hands:
        result = hand_rank(hand)
        assert not result["is_gutshot"], f"{hand} should NOT be a gutshot."


def test_no_gutshot_row():
    """Ensure a gutshot is NOT identified in a row."""
    row = pd.Series({
        "hole_cards": [CARDS["Ah"], CARDS["As"], CARDS["8c"], CARDS["3d"]],
        "community_cards": [CARDS["Ks"], CARDS["Qd"], CARDS["9c"], CARDS["6h"], CARDS["2s"]]
    })
    hand_results = categorize_hand(row)
    assert not hand_results["is_gutshot"], f"Gutshot detection failed for {row}."


def test_gutshot_row():
    """Ensure a gutshot is correctly identified in a row."""
    row = pd.Series({
        "hole_cards": [CARDS["5h"], CARDS["6d"], CARDS["7h"], CARDS["8h"]],
        "community_cards": [CARDS["7s"], CARDS["8c"], CARDS["Ts"], CARDS["2d"], CARDS["3s"]]
    })
    hand_results = categorize_hand(row)
    assert hand_results["is_gutshot"], f"Gutshot detection failed for {row}."


def test_straight_flush():
    """Ensure a correct straight flush is identified."""
    hand = [CARDS["5s"], CARDS["6s"], CARDS["7s"], CARDS["8s"], CARDS["9s"]]
    result = hand_rank(hand)
    assert result["is_straight_flush"], "5s6s7s8s9s should be a straight flush."


def test_straight_flush_row():
    """Ensure a straight flush is correctly identified in a row."""
    row = pd.Series({
        "hole_cards": [CARDS["5s"], CARDS["6s"], CARDS["7s"], CARDS["8s"]],
        "community_cards": [CARDS["7s"], CARDS["8s"], CARDS["9s"], CARDS["2d"], CARDS["3s"]]
    })
    hand_results = categorize_hand(row)
    assert hand_results["is_straight_flush"], f"Straight flush detection failed for {row}."


def test_flush():
    """Ensure a regular flush is correctly identified."""
    hand = [CARDS["2h"], CARDS["4h"], CARDS["6h"], CARDS["8h"], CARDS["Th"]]
    result = hand_rank(hand)
    assert result["is_flush"], "Flush detection failed for 2h4h6h8hTh."


def test_flush_row():
    """Ensure a flush is correctly identified in a row."""
    row = pd.Series({
        "hole_cards": [CARDS["2h"], CARDS["4h"], CARDS["6h"], CARDS["8h"]],
        "community_cards": [CARDS["6h"], CARDS["8h"], CARDS["Th"], CARDS["2d"], CARDS["3s"]]
    })
    hand_results = categorize_hand(row)
    assert hand_results["is_flush"], f"Flush detection failed for {row}."


def test_straight():
    """Ensure a straight is correctly identified."""
    hand = [CARDS["5d"], CARDS["6h"], CARDS["7c"], CARDS["8s"], CARDS["9h"]]
    result = hand_rank(hand)
    assert result["is_straight"], "5d6h7c8s9h should be a straight."


def test_straight_row():
    """Ensure a straight is correctly identified in a row."""
    row = pd.Series({
        "hole_cards": [CARDS["5d"], CARDS["6h"], CARDS["7c"], CARDS["8s"]],
        "community_cards": [CARDS["7c"], CARDS["8s"], CARDS["9h"], CARDS["2d"], CARDS["3s"]]
    })
    hand_results = categorize_hand(row)
    assert hand_results["is_straight"], f"Straight detection failed for {row}."


def test_straight_with_ace_low():
    """Ensure a straight with an ace low is correctly identified."""
    hand = [CARDS["Ad"], CARDS["2h"], CARDS["3c"], CARDS["4s"], CARDS["5h"]]
    result = hand_rank(hand)
    assert result["is_straight"], "Ad2h3c4s5h should be a straight."


def test_straight_with_ace_low_row():
    """Ensure a straight with an ace low is correctly identified in a row."""
    row = pd.Series({
        "hole_cards": [CARDS["Ad"], CARDS["2h"], CARDS["3c"], CARDS["4s"]],
        "community_cards": [CARDS["3c"], CARDS["4s"], CARDS["5h"], CARDS["6d"], CARDS["7s"]]
    })
    hand_results = categorize_hand(row)
    assert hand_results["is_straight"], f"Straight detection failed for {row}."


def test_full_house():
    """Ensure a full house is correctly identified."""
    hand = [CARDS["9h"], CARDS["9d"], CARDS["9s"], CARDS["6c"], CARDS["6h"]]
    result = hand_rank(hand)
    assert result["is_full_house"], "Full house detection failed for 9h9d9s6c6h."


def test_full_hours_row():
    """Ensure a full house is correctly identified in a row."""
    row = pd.Series({
        "hole_cards": [CARDS["9h"], CARDS["9d"], CARDS["6s"], CARDS["6c"]],
        "community_cards": [CARDS["9s"], CARDS["6c"], CARDS["6h"], CARDS["2d"], CARDS["3s"]]
    })
    hand_results = categorize_hand(row)
    assert hand_results["is_full_house"], f"Full house detection failed for {row}."


if __name__ == "__main__":
    # pytest.main()
    test_gutshot_row()
