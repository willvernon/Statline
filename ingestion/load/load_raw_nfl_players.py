import nflreadpy as nfl

from ingestion.ducklake import get_connection


def main() -> None:
    players = nfl.load_players()

    with get_connection() as conn:
        conn.register('players', players)
        conn.sql('DELETE FROM lake.raw.nfl_players')
        conn.sql(
            """
            INSERT INTO lake.raw.nfl_players
            SELECT *
            FROM players
        """
        )

        result = conn.sql('SELECT COUNT(*) FROM lake.raw.nfl_players').fetchone()
        if result is None:
            raise RuntimeError('COUNT(*) returned no rows')
        print(f'Loaded {result[0]} rows into lake.raw.nfl_players')


if __name__ == '__main__':
    main()
