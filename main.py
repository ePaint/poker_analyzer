import argparse
import os
import time
from pathlib import Path

import polars

from logger.logger import INFO, ENDC, DEBUG, ERROR
from src.plotter import plot_chart
from src.settings import SETTINGS


def file_picker():
    """
    Prompts the user to select a file from a list of files in the current directory.
    Returns the selected file path.
    If the user enters 'r', it returns None, for reading files in the input folder.
    """
    files = []
    for file in os.listdir(path=SETTINGS.OUTPUT_FOLDER):
        if not file.startswith("parsed_") or not file.endswith(".parquet"):
            continue
        files.append(file)
    if not files:
        return None

    print(f"{DEBUG}Select a file:{ENDC}")
    for i, file in enumerate(files):
        print(f"{DEBUG}{i + 1}){ENDC} {file}")

    print(f"{DEBUG}r){ENDC} {INFO}Read files in input folder{ENDC}")

    while True:
        choice = input(f"{DEBUG}Enter the number of the file you want to select: {ENDC}")
        if choice == "r":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            choice = int(choice) - 1
            break
        print(f"{ERROR}Invalid choice. Please try again.{ENDC}")
    return SETTINGS.OUTPUT_FOLDER / files[choice]


def main():
    parser = argparse.ArgumentParser(description="Process a file path.")
    parser.add_argument(
        "--file", required=False, type=Path, help="Path to the input file"
    )

    args = parser.parse_args()

    if args.file is None:
        args.file = file_picker()

    if args.file is not None and not args.file.exists():
        raise FileNotFoundError(f"File {args.file} does not exist.")

    plot_chart(file=args.file)


if __name__ == "__main__":
    os.environ["POLARS_MAX_THREADS"] = "16"
    polars.Config.set_tbl_width_chars(300).set_fmt_table_cell_list_len(10)
    start = time.time()
    main()
    print(f"Finished in {time.time() - start:.3f} seconds")
