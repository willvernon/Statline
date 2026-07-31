import nflreadpy as nfl

from ingestion.ducklake import get_connection


def main(season: int | None = None) -> None:
    if season is None:
        season = nfl.get_current_season()
    schedules = nfl.load_schedules(seasons=season)

    with get_connection() as conn:
        conn.register('schedules', schedules)
        conn.sql(f'DELETE FROM lake.raw.nfl_schedules WHERE season = {season}')
        conn.sql("""
            INSERT INTO lake.raw.nfl_schedules BY NAME
            SELECT *
            FROM schedules
        """)

        result = conn.sql(
            f'SELECT COUNT(*) FROM lake.raw.nfl_schedules WHERE season = {season}'
        ).fetchone()
        if result is None:
            raise RuntimeError('COUNT(*) returned no rows')
        print(f'Loaded {result[0]} rows into lake.raw.nfl_schedules')


if __name__ == '__main__':
    main()
