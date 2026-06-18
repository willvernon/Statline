import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv


SCHEMA_PATH = Path(__file__).parent / "schemas" / "Statline_Schema.sql"


def initialize_ducklake() -> None:
    load_dotenv()

    lake_catalog = os.environ["LAKE_CATALOG_PATH"]
    lake_data_path = os.environ["LAKE_DATA_PATH"]

    with duckdb.connect() as con:
        con.sql(
            f"ATTACH 'ducklake:{lake_catalog}' AS lake "
            f"(DATA_PATH '{lake_data_path}')"
        )
        con.sql("CREATE SCHEMA IF NOT EXISTS lake.raw")
        con.sql(SCHEMA_PATH.read_text())


if __name__ == "__main__":
    initialize_ducklake()
