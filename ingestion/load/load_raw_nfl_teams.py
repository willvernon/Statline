import nflreadpy as nfl

from ingestion.ducklake import get_connection


def main() -> None:
    teams = nfl.load_teams()

    with get_connection() as conn:
        conn.register('teams', teams)
        conn.sql("""
            INSERT INTO lake.raw.nfl_teams
            SELECT *
            FROM teams
        """)

        result = conn.sql('SELECT COUNT(*) FROM lake.raw.nfl_teams').fetchone()
        if result is None:
            raise RuntimeError('COUNT(*) returned no rows')
        print(f'Loaded {result[0]} rows into lake.raw.nfl_teams')


if __name__ == '__main__':
    main()
