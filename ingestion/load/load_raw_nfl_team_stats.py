import nflreadpy as nfl

from ingestion.ducklake import get_connection


def main() -> None:
    team_stats = nfl.load_team_stats(seasons=True)

    with get_connection() as conn:
        conn.register('team_stats', team_stats)
        conn.sql("""
            INSERT INTO lake.raw.nfl_team_stats
            SELECT *
            FROM team_stats
        """)

        result = conn.sql('SELECT COUNT(*) FROM lake.raw.nfl_team_stats').fetchone()
        if result is None:
            raise RuntimeError('COUNT(*) returned no rows')
        print(f'Loaded {result[0]} rows into lake.raw.nfl_team_stats')


if __name__ == '__main__':
    main()
