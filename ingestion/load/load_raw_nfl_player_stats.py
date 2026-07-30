import nflreadpy as nfl

from ingestion.ducklake import get_connection


def main(season: int | None = None) -> None:
    if season is None:
        season = nfl.get_current_season()
    player_stats = nfl.load_player_stats(seasons=season)

    with get_connection() as conn:
        conn.register('player_stats', player_stats)
        conn.sql(f'DELETE FROM lake.raw.nfl_player_stats WHERE season = {season}')
        conn.sql("""
            INSERT INTO lake.raw.nfl_player_stats BY NAME
            SELECT *
            FROM player_stats
        """)

        result = conn.sql(
            f'SELECT COUNT(*) FROM lake.raw.nfl_player_stats WHERE season = {season}'
        ).fetchone()
        if result is None:
            raise RuntimeError('COUNT(*) returned no rows')
        print(
            f'Loaded {result[0]} rows into lake.raw.nfl_player_stats for season {season}'
        )


if __name__ == '__main__':
    main()
