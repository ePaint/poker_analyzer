import os
import time
from functools import lru_cache

import polars

from logger import logger
from src.settings import SETTINGS
from src.models.File import File


def mark_as_processed(
    folder_name: str,
    file_name: str,
) -> None:
    if not SETTINGS.MOVE_FILES_TO_PROCESSED_FOLDER:
        return
    if SETTINGS.ADD_TIMESTAMP_TO_PROCESSED_FILES:
        destination_file = f"{folder_name}/processed/{SETTINGS.TIMESTAMP}_{file_name}"
    else:
        destination_file = f"{folder_name}/processed/{file_name}"
    os.rename(src=f"{folder_name}/{file_name}", dst=destination_file)


RANK_ORDER = "23456789TJQKA"  # For sorting ranks
REVERSED_RANK_ORDER = RANK_ORDER[::-1]  # For reversed order


@lru_cache(maxsize=None)
def get_rank_index(rank: str) -> int:
    try:
        return RANK_ORDER.index(rank)
    except ValueError:
        logger.error(f"Invalid rank: {rank}")
        raise ValueError(f"Invalid rank: {rank}. Valid ranks are: {RANK_ORDER}")


def read_file(file: File, lazy: bool = False, head: int = None) -> polars.DataFrame | polars.LazyFrame:
    logger.debug(f"Reading file: {file}")
    start = time.time()
    dataframe = polars.read_csv(file.path, has_header=False)
    if lazy:
        dataframe = dataframe.lazy()
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    if head:
        dataframe = dataframe.head(head)

    logger.debug("Generating index column")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.arange(0, polars.count(), dtype=polars.UInt32)
        .alias("row_idx")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Adding action column")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.lit(file.action)
        .cast(polars.Categorical)
        .alias("action")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Splitting data into weight and hole card. Adding community cards and community card combos")
    start = time.time()
    dataframe = (
        dataframe.with_columns(
            polars.col("column_1")
            .str.split_exact(":", 1)
            .struct.rename_fields(["weight", "hole_cards"])
            .struct.unnest()
        )
        .with_columns(polars.col("weight").cast(polars.Float32, strict=False))
        .drop("column_1")
        .with_columns(
            polars.col("hole_cards")
            .str.extract_all(r"([2-9TJQKA][hdcs])")
            .alias("hole_cards")
        )
        .with_columns(polars.lit(file.cards).alias("community_cards"))
        .with_columns(polars.lit(file.combos).alias("community_combos"))
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Generating hole cards ranks")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("hole_cards")
        .list.join("")
        .str.extract_all(r"([2-9TJQKA])")
        .list.sort(descending=True)
        .list.join("")
        .alias("hole_cards_ranks")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Generate community card combinations")
    start = time.time()
    hole_combos = (
        dataframe.select(["hole_cards"])
        .with_columns(polars.arange(0, polars.len()).alias("row_idx"))
        .explode("hole_cards")
        .rename({"hole_cards": "card_1"})
        .join(
            dataframe.explode("hole_cards").rename({"hole_cards": "card_2"}),
            on="row_idx",
        )
        .filter(polars.col("card_1") < polars.col("card_2"))
        .group_by("row_idx")
        .agg(
            polars.concat_list(["card_1", "card_2"]).alias("hole_combos")
        )
    )
    dataframe = dataframe.join(hole_combos, on="row_idx")
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Exploding hole and community card combinations")
    start = time.time()
    dataframe = (
        dataframe.explode("community_combos")
        .explode("hole_combos")
        .rename({"community_combos": "community_hand", "hole_combos": "hole_hand"})
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Creating hole hand ranks")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("hole_hand")
        .list.join("")
        .str.extract_all(r"([2-9TJQKA])")
        .list.eval(
            polars.element().replace({"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14})
        )
        .cast(polars.List(polars.UInt8))
        .alias("hole_hand_ranks")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Creating hand")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.concat_list(["hole_hand", "community_hand"])
        .list.sort()
        .list.join("")
        .alias("hand")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    return dataframe


def apply_poker_hands(
    poker_hands: polars.DataFrame, dataframe: polars.DataFrame
) -> polars.DataFrame:
    dataframe = dataframe.join(
        poker_hands,
        left_on="hand",
        right_on="hand",
        how="left",
    )

    return dataframe


def calculate_flush_draws(dataframe: polars.DataFrame) -> polars.DataFrame:
    def flush_level(hand: list[str], board: list[str]) -> int:
        suits = ["s", "h", "d", "c"]

        for suit in suits:
            hand_suit_cards = [card for card in hand if card.endswith(suit)]
            hand_ranks = set(card[0] for card in hand_suit_cards)
            board_suit_cards = [card for card in board if card.endswith(suit)]
            board_ranks = set(card[0] for card in board_suit_cards)

            if len(hand_suit_cards) >= 2 and len(board_suit_cards) >= 2:
                known_ranks = set(card[0] for card in hand_suit_cards + board_suit_cards)

                highest_board_rank_index = 0
                while True:
                    highest_possible_rank = REVERSED_RANK_ORDER[highest_board_rank_index]
                    if highest_possible_rank in board_ranks:
                        highest_board_rank_index += 1
                    else:
                        break

                if REVERSED_RANK_ORDER[highest_board_rank_index] in hand_ranks:
                    return 1  # Nut flush draw
                elif REVERSED_RANK_ORDER[highest_board_rank_index+1] in hand_ranks and REVERSED_RANK_ORDER[highest_board_rank_index] not in known_ranks:
                    return 2  # 2nd Nut flush draw
                elif REVERSED_RANK_ORDER[highest_board_rank_index+2] in hand_ranks and all(x not in known_ranks for x in [REVERSED_RANK_ORDER[highest_board_rank_index], REVERSED_RANK_ORDER[highest_board_rank_index+1]]):
                    return 3  # 3rd Nut flush draw
                else:
                    return 4  # Low flush draw

        return 9  # No flush draw

    logger.debug("Calculating flush draws")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.struct(["hole_hand", "community_hand"]).map_elements(
            lambda row: flush_level(row["hole_hand"], row["community_hand"]),
            return_dtype=polars.UInt8
        ).alias("flush_draw")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating flush ranks")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.when(polars.col("is_flush"))
        .then(polars.col("hole_hand_ranks").list.max())
        .otherwise(None)
        .alias("flush_rank")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    return dataframe


def _get_straight_draw_ranks(is_straight: bool, hole_hand: list[str], community_hand: list[str]) -> list[str]:
    if is_straight:
        return []

    hole_indices = {get_rank_index(card[0]) for card in hole_hand}
    if len(hole_indices) < 2 or max(hole_indices) - min(hole_indices) > 4:
        return []

    community_indices = {get_rank_index(card[0]) for card in community_hand}
    outs = set()

    for index in community_indices:
        other_indices = community_indices.copy()
        if len(other_indices) == 1:
            continue
        if len(community_indices) == 3:
            other_indices -= {index}
        indices = hole_indices.union(other_indices)
        for replacement in range(0, 13):
            new_indices = indices.union({replacement})
            if len(new_indices) == 5 and max(new_indices) - min(new_indices) == 4:
                outs.add(RANK_ORDER[replacement])

    return sorted(outs, key=get_rank_index)


def calculate_straight_draw_ranks(dataframe: polars.DataFrame) -> polars.DataFrame:
    logger.debug("Calculating straight draw ranks")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.struct(["is_straight", "hole_hand", "community_hand"]).map_elements(
            lambda row: _get_straight_draw_ranks(
                is_straight=row["is_straight"],
                hole_hand=row["hole_hand"],
                community_hand=row["community_hand"],
            ),
            return_dtype=polars.List(polars.Utf8)
        ).alias("draw_straight_ranks")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    return dataframe


def collapse_on_index(dataframe: polars.DataFrame) -> polars.DataFrame:
    logger.debug("Collapsing dataframe on row index")
    dataframe = dataframe.group_by("row_idx").agg(
        polars.col("action").first(),
        polars.col("weight").first(),
        polars.col("community_cards").first(),
        polars.col("hole_cards").first(),
        polars.col("hole_cards_ranks").first(),
        polars.col("is_flush").any(),
        polars.col("is_straight").any(),
        polars.col("is_straight_flush").any(),
        polars.col("is_pair").any(),
        polars.col("is_two_pair").any(),
        polars.col("is_trips").any(),
        polars.col("is_quads").any(),
        polars.col("is_full_house").any(),
        polars.col("pair_rank").flatten(),
        polars.col("full_house_pair_rank").filter(polars.col("is_full_house")).unique().reverse(),
        polars.col("flush_rank").max(),
        polars.col("straight_rank").filter(polars.col("is_straight")).max(),
        polars.col("set_rank").filter(polars.col("is_trips")).unique().reverse(),
        polars.col("best_hand_value").min(),
        polars.col("flush_draw").min(),
        polars.col("draw_straight_ranks").list.unique().alias("draw_straight_ranks"),
    )

    dataframe = dataframe.with_columns(
        polars.col("pair_rank")
        .list.max()
    )

    dataframe = dataframe.with_columns(
        polars.col("best_hand_value")
        .cast(polars.String)
        .str.replace("1", "Straight Flush")
        .str.replace("2", "Flush")
        .str.replace("3", "Straight")
        .str.replace("4", "Four of a Kind")
        .str.replace("5", "Full House")
        .str.replace("6", "Three of a Kind")
        .str.replace("7", "Two Pair")
        .str.replace("8", "One Pair")
        .str.replace("9", "High Card")
        .alias("best_hand")
    )

    dataframe = dataframe.with_columns(
        polars.col("flush_draw")
        .cast(polars.String)
        .str.replace("1", "Nut Flush Draw")
        .str.replace("2", "2nd Nut Flush Draw")
        .str.replace("3", "3rd Nut Flush Draw")
        .str.replace("4", "Low Flush Draw")
        .str.replace("9", "No Flush Draw")
        .alias("flush_draw")
    )

    dataframe = dataframe.drop("row_idx")
    return dataframe


def calculate_straight_draw_outs(dataframe: polars.DataFrame) -> polars.DataFrame:
    def count_unique_flat_ranks(nested_lists: list[list[str]]) -> list[str]:
        return list(set(rank for sublist in nested_lists for rank in sublist))

    dataframe = dataframe.with_columns(
        polars.struct(["draw_straight_ranks"])
        .map_elements(
            lambda row: count_unique_flat_ranks(row["draw_straight_ranks"]),
            return_dtype=polars.List(polars.String),
        )
        .alias("draw_straight_ranks")
    )

    def count_straight_outs(draw_ranks: list[str],
                            hole_cards: list[str],
                            community_cards: list[str]) -> int:
        if not draw_ranks:
            return 0

        known_cards = hole_cards + community_cards
        known_ranks = [card[0] for card in known_cards]  # Assuming format like "9♣", "T♠", etc.

        total_outs = 0
        for rank in draw_ranks:
            used = known_ranks.count(rank)
            remaining = max(0, 4 - used)
            total_outs += remaining

        return total_outs

    dataframe = dataframe.with_columns(
        polars.struct(["draw_straight_ranks", "hole_cards", "community_cards"])
        .map_elements(
            lambda row: count_straight_outs(
                draw_ranks=row["draw_straight_ranks"],
                hole_cards=row["hole_cards"],
                community_cards=row["community_cards"]
            ),
            return_dtype=polars.UInt8
        ).alias("draw_straight_outs")
    )

    return dataframe


def re_order_columns(dataframe: polars.DataFrame) -> polars.DataFrame:
    columns_order = [
        "action",
        "weight",
        "community_cards",
        "hole_cards",
        "hole_cards_ranks",
        "is_flush",
        "is_straight",
        "is_straight_flush",
        "is_pair",
        "is_two_pair",
        "is_trips",
        "is_quads",
        "is_full_house",
        "pair_rank",
        "full_house_pair_rank",
        "flush_rank",
        "straight_rank",
        "set_rank",
        "best_hand_value",
        "best_hand",
        "flush_draw",
        "draw_straight_ranks",
        "draw_straight_outs",
    ]
    dataframe = dataframe.select(columns_order)
    return dataframe


def save_to_csv(dataframe: polars.DataFrame, filename: str) -> None:
    for column in dataframe.columns:
        schema = dataframe.schema[column]
        logger.debug(f"Flattening column: {column} with schema: {schema}")
        if schema == polars.List(polars.String):
            dataframe = dataframe.with_columns(
                polars.col(column)
                .list.join(',')
            )
        elif schema == polars.List:
            dataframe = dataframe.with_columns(
                polars.col(column)
                .cast(polars.List(polars.String))
                .list.join(',')
            )
    dataframe.write_csv(filename)


def read_input_files(lazy: bool = False, head: int = None) -> polars.DataFrame | None:
    files = []
    for filepath in SETTINGS.INPUT_FOLDER.iterdir():
        if not SETTINGS.INPUT_FILE_REGEX.match(filepath.name.casefold()):
            continue
        logger.info(f"Reading file: {filepath}")
        files.append(File(filepath))

    poker_hands = polars.read_parquet("poker_hands.parquet")
    output = None
    for file in files:
        logger.info(f"Processing: {file}")

        dataframe = read_file(file=file, lazy=lazy, head=head)
        dataframe = apply_poker_hands(poker_hands=poker_hands, dataframe=dataframe)
        dataframe = calculate_flush_draws(dataframe=dataframe)
        dataframe = calculate_straight_draw_ranks(dataframe=dataframe)
        dataframe = collapse_on_index(dataframe=dataframe)
        dataframe = calculate_straight_draw_outs(dataframe=dataframe)
        dataframe = re_order_columns(dataframe=dataframe)

        if output is None:
            output = dataframe
        else:
            output = output.vstack(dataframe)

    if output is not None:
        cards = "".join(files[0].cards)
        actions = "-".join(file.action.title() for file in files)
        filename = f"{SETTINGS.OUTPUT_FOLDER}/parsed_{SETTINGS.TIMESTAMP_LABEL}_{cards}_{actions}"
        if SETTINGS.SAVE_CACHE:
            output.write_parquet(f"{filename}.parquet")
        if SETTINGS.SAVE_CACHE_COPY_AS_CSV:
            save_to_csv(dataframe=output, filename=f"{filename}.csv")

    return output
