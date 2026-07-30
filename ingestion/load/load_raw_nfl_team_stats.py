import nflreadpy as nfl

from ingestion.ducklake import get_connection


def main(season: int | None = None) -> None:
    if season is None:
        season = nfl.get_current_season()
    team_stats = nfl.load_team_stats(seasons=season)

    with get_connection() as conn:
        conn.register('team_stats', team_stats)
        conn.sql(f'DELETE FROM lake.raw.nfl_team_stats WHERE season = {season}')
        conn.sql("""
            INSERT INTO lake.raw.nfl_team_stats BY NAME
            SELECT *
            FROM team_stats
        """)

        result = conn.sql(
            f'SELECT COUNT(*) FROM lake.raw.nfl_team_stats WHERE season = {season}'
        ).fetchone()
        if result is None:
            raise RuntimeError('COUNT(*) returned no rows')
        print(f'Loaded {result[0]} rows into lake.raw.nfl_team_stats')


if __name__ == '__main__':
    main()
