import json
import os
import time
from itertools import combinations

import polars

from logger import logger
from src.models.KPI import BEST_HANDS
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


def generate_hands(hole_cards, community_cards):
    # Generate all combinations of 2 hole cards and 3 community cards
    hole_combinations = list(combinations(hole_cards, 2))
    community_combinations = list(combinations(community_cards, 3))

    # Combine them into 5-card hands
    hands = [
        list(hole) + list(community)
        for hole in hole_combinations
        for community in community_combinations
    ]
    return hands


def generate_combinations(items: list, n: int) -> list:
    return list(combinations(items, n))


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
        .with_columns(
            polars.col("weight")
            .cast(polars.Float32, strict=False)
        )
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

    logger.debug("Generate community card combinations")
    start = time.time()
    community_combos = (
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
    dataframe = dataframe.join(community_combos, on="row_idx")
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
        polars.concat_list(["hole_hand", "community_hand"]).alias("hand")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    return dataframe


def analyze_data(
    dataframe: polars.DataFrame | polars.LazyFrame,
) -> polars.DataFrame | polars.LazyFrame:
    logger.debug("Generating hand string")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("hand").list.join("").alias("hand_str")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Generating ranks")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("hand_str").str.extract_all(r"([2-9TJQKA])").alias("ranks")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Generating suits")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("hand_str").str.extract_all(r"([hdcs])").alias("suits")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Dropping hand_str column")
    start = time.time()
    dataframe = dataframe.drop("hand_str")
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating number of unique ranks")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("ranks")
        .list.n_unique()
        .alias("num_unique_ranks")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating ranks")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("ranks")
        .list.eval(polars.element().replace({"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}))
        .cast(polars.List(polars.UInt8))
        .list.sort()
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating reversed ranks")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("ranks")
        .list.eval(
            polars.when(polars.element().eq(14)).then(1).otherwise(polars.element())
        )
        .list.sort()
        .alias("ranks_reversed")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating unique_ranks")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("ranks")
        .list.unique()
        .alias("unique_ranks")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating rank counts")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("ranks")
        .list.eval(
            polars.element().unique_counts()
        )
        .alias("rank_counts")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating number of unique suits")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("suits")
        .list.n_unique()
        .alias("num_unique_suits")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating rank difference")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("ranks")
        .list.eval(polars.element().max() - polars.element().min())
        .list.first()
        .alias("rank_difference")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    return dataframe


def construct_poker_results(
    dataframe: polars.DataFrame | polars.LazyFrame,
) -> polars.DataFrame | polars.LazyFrame:
    logger.debug("Calculating is_flush")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("num_unique_suits").eq(1).alias("is_flush")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating is_straight")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("num_unique_ranks")
        .eq(5)
        .and_(polars.col("rank_difference").eq(4))
        .alias("is_straight")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating is_straight_flush")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("is_straight")
        .and_(polars.col("is_flush"))
        .alias("is_straight_flush")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating is_pair")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("rank_counts")
        .list.contains(2)
        .alias("is_pair")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating is_two_pair")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("is_pair")
        .eq(True)
        .and_(polars.col("rank_counts").list.len().eq(3))
        .alias("is_two_pair")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating is_trips")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("rank_counts")
        .list.contains(3)
        .alias("is_trips")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating is_quads")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("rank_counts")
        .list.contains(4)
        .alias("is_quads")
    )
    logger.debug(f"Done in {time.time() - start:.2f} seconds")

    logger.debug("Calculating is_full_house")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.col("is_trips").and_(polars.col("is_pair")).alias("is_full_house")
    )
    logger.debug(f"Done in {time.time() - start:.3f} seconds")

    logger.debug("Calculating pair_rank")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.when(polars.col("is_pair"))
        .then(
            polars.col("unique_ranks")
            .list.get(
                polars.col("rank_counts")
                .list.eval(polars.element().index_of(polars.lit(2, dtype=polars.UInt8)))
                .list.first()
            )
        )
        .otherwise(polars.lit(None))
        .alias("pair_rank")
    )
    logger.debug(f"Done in {time.time() - start:.3f} seconds")

    logger.debug("Calculating full_house_pair_rank")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.when(polars.col("is_full_house"))
        .then(
            polars.col("pair_rank")
        )
        .otherwise(polars.lit(None))
        .alias("full_house_pair_rank")
    )
    logger.debug(f"Done in {time.time() - start:.3f} seconds")

    logger.debug("Calculating flush_rank")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.when(polars.col("is_flush"))
        .then(
            polars.col("unique_ranks")
            .list.min()
        )
        .otherwise(polars.lit(None))
        .alias("flush_rank")
    )
    logger.debug(f"Done in {time.time() - start:.3f} seconds")

    logger.debug("Calculating straight_rank")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.when(polars.col("is_straight"))
        .then(
            polars.col("unique_ranks")
            .list.min()
        )
        .otherwise(polars.lit(None))
        .alias("straight_rank")
    )
    logger.debug(f"Done in {time.time() - start:.3f} seconds")

    logger.debug("Calculating set_rank")
    start = time.time()
    dataframe = dataframe.with_columns(
        polars.when(polars.col("is_trips"))
        .then(
            polars.col("unique_ranks")
            .list.get(
                polars.col("rank_counts")
                .list.eval(polars.element().index_of(polars.lit(3, dtype=polars.UInt8)))
                .list.first()
            )
        )
        .otherwise(polars.lit(None))
        .alias("set_rank")
    )
    logger.debug(f"Done in {time.time() - start:.3f} seconds")

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
    )
    dataframe = dataframe.drop("row_idx")
    return dataframe


def assign_best_hand(dataframe: polars.DataFrame) -> polars.DataFrame:
    dataframe = dataframe.with_columns([
        polars.when(polars.col("is_straight_flush"))
        .then(polars.lit(BEST_HANDS["is_straight_flush"]))
        .when(polars.col("is_quads"))
        .then(polars.lit(BEST_HANDS["is_quads"]))
        .when(polars.col("is_full_house"))
        .then(polars.lit(BEST_HANDS["is_full_house"]))
        .when(polars.col("is_flush"))
        .then(polars.lit(BEST_HANDS["is_flush"]))
        .when(polars.col("is_straight"))
        .then(polars.lit(BEST_HANDS["is_straight"]))
        .when(polars.col("is_trips"))
        .then(polars.lit(BEST_HANDS["is_trips"]))
        .when(polars.col("is_two_pair"))
        .then(polars.lit(BEST_HANDS["is_two_pair"]))
        .when(polars.col("is_pair"))
        .then(polars.lit(BEST_HANDS["is_pair"]))
        .otherwise(polars.lit("High Card"))
        .alias("best_hand")
    ])
    return dataframe


def save_to_csv(dataframe: polars.DataFrame, filename: str) -> None:
    dataframe = dataframe.with_columns(
        polars.col("community_cards").list.join(','),
        polars.col("hole_cards").list.join(','),
        polars.col("pair_rank").cast(polars.List(polars.String)).list.join(','),
        polars.col("full_house_pair_rank").cast(polars.List(polars.String)).list.join(','),
        polars.col("flush_rank").cast(polars.List(polars.String)).list.join(','),
        polars.col("straight_rank").cast(polars.List(polars.String)).list.join(','),
        polars.col("set_rank").cast(polars.List(polars.String)).list.join(','),
    )
    dataframe.write_csv(filename)


def read_input_files(lazy: bool = False, head: int = None) -> polars.DataFrame | None:
    files = []
    for filepath in SETTINGS.INPUT_FOLDER.iterdir():
        if not SETTINGS.INPUT_FILE_REGEX.match(filepath.name.casefold()):
            continue
        logger.info(f"Reading file: {filepath}")
        files.append(File(filepath))

    output = None
    for file in files:
        logger.info(f"Processing: {file}")

        dataframe = read_file(file=file, lazy=lazy, head=head)
        dataframe = analyze_data(dataframe=dataframe)
        dataframe = construct_poker_results(dataframe=dataframe)
        dataframe = collapse_on_index(dataframe=dataframe)
        dataframe = assign_best_hand(dataframe=dataframe)

        if output is None:
            output = dataframe
        else:
            output = output.vstack(dataframe)

    if output is not None:
        cards = "".join(files[0].cards)
        actions = "-".join(file.action.title() for file in files)
        filename = f"{SETTINGS.OUTPUT_FOLDER}/parsed_{SETTINGS.TIMESTAMP_LABEL}_{cards}_{actions}"
        output.write_parquet(f"{filename}.parquet")
        if SETTINGS.SAVE_PARSED_AS_CSV:
            save_to_csv(dataframe=output, filename=f"{filename}.csv")

    return output
