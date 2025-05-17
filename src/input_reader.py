import os
import time

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
        polars.arange(0, polars.count()).alias("row_idx")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Adding action column")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.lit(file.action).alias("action")
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
        .list.eval(
            polars.element().replace({"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14})
        )
        .cast(polars.List(polars.UInt8))
        .list.unique()
        .list.sort()
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
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Joining community card combinations")
    start = time.time()
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

    logger.debug("Combining hole and community card combinations")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.concat_list(["hole_hand", "community_hand"])
        .list.sort()
        .list.join("")
        .alias("hand")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    # NOTES TO SELF:
    # TODO:
    # - Right now, the code is 99% working but we need to compare the ranks instead of the actual cards.
    # - First, calculate the ranks of the hole cards and the hand cards
    # - Then, compare the ranks instead of the cards.

    logger.debug("Generating hole hand ranks")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("hole_hand")
        .list.join("")
        .str.extract_all(r"([2-9TJQKA])")
        .list.eval(
            polars.element().replace({"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14})
        )
        .cast(polars.List(polars.UInt8))
        .list.unique()
        .list.sort()
        .alias("hole_hand_ranks")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    # logger.debug("Sorting hole_hand")
    # start = time.time()
    # dataframe = dataframe.with_columns(
    #     polars.col("hole_hand").list.sort().alias("hole_hand")
    # )
    # logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Generating first_two_match")
    start = time.time()
    dataframe = dataframe.with_columns(
        (
            polars.col("hole_cards_ranks").list.slice(-2, 2) == polars.col("hole_hand_ranks")
        )
        .alias("first_two_match")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Generating second_two_match")
    start = time.time()
    dataframe = dataframe.with_columns(
        (
            polars.col("hole_cards_ranks").list.slice(-3, 2) == polars.col("hole_hand_ranks")
        )
        .alias("second_two_match")
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

    dataframe = dataframe.with_columns(
        polars.when(
            polars.col("draw_flush_rank").ne(0),
        )
        .then(
            polars.when(
                polars.col("first_two_match"),
            )
            .then(1)
            .otherwise(
                polars.when(
                    polars.col("second_two_match")
                )
                .then(2)
                .otherwise(3)
            )
        )
        .otherwise(None)
        .alias("draw_flush_rank"),
    )

    return dataframe


def collapse_on_index(dataframe: polars.DataFrame) -> polars.DataFrame:
    dataframe = dataframe.group_by("row_idx").agg(
        polars.col("action").first(),
        polars.col("weight").first(),
        polars.col("community_cards").first(),
        polars.col("hole_cards").first(),
        polars.col("is_flush").any(),
        polars.col("is_straight").any(),
        polars.col("is_straight_flush").any(),
        polars.col("is_pair").any(),
        polars.col("is_two_pair").any(),
        polars.col("is_trips").any(),
        polars.col("is_quads").any(),
        polars.col("is_full_house").any(),
        polars.col("pair_rank").filter(polars.col("is_pair")).unique().reverse(),
        polars.col("full_house_pair_rank").filter(polars.col("is_full_house")).unique().reverse(),
        polars.col("flush_rank").filter(polars.col("is_flush")).unique().reverse(),
        polars.col("straight_rank").filter(polars.col("is_straight")).unique().reverse(),
        polars.col("set_rank").filter(polars.col("is_trips")).unique().reverse(),
        polars.col("best_hand_value").min(),
        polars.col("draw_straight_outs").sum(),
        polars.col("draw_flush_rank").min(),
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
    dataframe = dataframe.drop("row_idx")
    return dataframe


def save_to_csv(dataframe: polars.DataFrame, filename: str) -> None:
    for column in dataframe.columns:
        if dataframe.schema[column] == polars.List:
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
        dataframe = collapse_on_index(dataframe=dataframe)

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
