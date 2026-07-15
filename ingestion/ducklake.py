import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv
from contextlib import contextmanager


SCHEMA_PATH = Path(__file__).parent / 'schemas' / 'Statline_Schema.sql'


def initialize_ducklake() -> None:
    load_dotenv()

    lake_catalog = os.environ['LAKE_CATALOG_PATH']
    lake_data_path = os.environ['LAKE_DATA_PATH']

    with duckdb.connect() as conn:
        conn.sql(
            f"ATTACH 'ducklake:{lake_catalog}' AS lake (DATA_PATH '{lake_data_path}')"
        )
        conn.sql('CREATE SCHEMA IF NOT EXISTS lake.raw')
        conn.sql(SCHEMA_PATH.read_text())
    print('DuckLake initialized: schema and tables created')


@contextmanager
def get_connection():
    """Yield a DuckDB connection with the DuckLake already attached.

    Usage:
        with get_connection() as conn:
            conn.sql("INSERT INTO lake.raw.dim_team ...")
    """
    load_dotenv()

    lake_catalog = os.environ['LAKE_CATALOG_PATH']
    lake_data_path = os.environ['LAKE_DATA_PATH']

    conn = duckdb.connect()
    try:
        conn.sql(
            f"ATTACH 'ducklake:{lake_catalog}' AS lake (DATA_PATH '{lake_data_path}')"
        )
        yield conn
    finally:
        conn.close()


if __name__ == '__main__':
    initialize_ducklake()
