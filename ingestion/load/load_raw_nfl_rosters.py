import nflreadpy as nfl

from ingestion.ducklake import get_connection


def main() -> None:
    season = nfl.get_current_season()
    # week = nfl.get_curent_week()

    rosters = nfl.load_rosters(seasons=season)
    with get_connection() as conn:
        conn.register('rosters', rosters)
        conn.sql(f'DELETE FROM lake.raw.nfl_rosters WHERE season = {season}')
        conn.sql("""
            INSERT INTO lake.raw.nfl_rosters BY NAME
            SELECT *
            FROM rosters
        """)

        result = conn.sql(
            f'SELECT COUNT(*) FROM lake.raw.nfl_rosters WHERE season = {season}'
        ).fetchone()
        if result is None:
            raise RuntimeError('COUNT(*) returned no rows')
        print(f'Loaded {result[0]} rows into lake.raw.nfl_rosters')


if __name__ == '__main__':
    main()
