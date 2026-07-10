import nflreadpy as nfl

from ingestion.ducklake import get_connection


def main() -> None:
    rosters = nfl.load_rosters()

    with get_connection() as conn:
        conn.register('rosters', rosters)
        conn.sql("""
            INSERT INTO lake.raw.nfl_rosters
            SELECT *
            FROM rosters
        """)

        result = conn.sql('SELECT COUNT(*) FROM lake.raw.nfl_rosters').fetchone()
        if result is None:
            raise RuntimeError('COUNT(*) returned no rows')
        print(f'Loaded {result[0]} rows into lake.raw.nfl_rosters')


if __name__ == '__main__':
    main()
