import logging
import sqlite3
from pathlib import Path

import pandas as pd

from etl.settings import DATA_PATH

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(message)s")


def process_csv_file_to_df(csv_path: Path):
    """
    Process a CSV file, so it can be converted to a SQL database.
    """
    csv_df = pd.read_csv(csv_path)
    csv_df.table_name = csv_path.stem.replace("-", "_")

    return csv_df


def build_dataset_database(
    dataset_path: Path,
    root_path: Path,
):
    """
    Build the SQLite database from the CSV in the dataset_path.
    """
    dataset_slug = dataset_path.name
    logger.info(f"Started building the dataset for {dataset_slug}")

    db_path = root_path / f"{dataset_slug}.db"
    connection = sqlite3.connect(db_path)

    data_frames = []

    for csv_path in dataset_path.glob("*.csv"):
        logger.info(f"Found CSV file {csv_path.name}")
        data_frames.append(process_csv_file_to_df(csv_path=csv_path))

    for df in data_frames:
        table_exists = connection.execute(
            """
            SELECT COUNT(1) FROM sqlite_master WHERE type="table" AND name=?
            """,
            [df.table_name],
        ).fetchone()[0]

        if table_exists:
            connection.execute(f"DROP TABLE [{df.table_name}]")

        df.to_sql(df.table_name, connection, if_exists="append", index=False)


def main():
    for dataset_path in DATA_PATH.iterdir():
        # If it's not a directory then we know it's not a dataset.
        if dataset_path.is_dir() is False:
            continue

        # If the directory is hidden we should just ignore it and move on to
        # the next one.
        if dataset_path.name.startswith(".") is True:
            continue

        build_dataset_database(
            dataset_path=dataset_path,
            root_path=DATA_PATH,
        )


if __name__ == "__main__":
    main()
