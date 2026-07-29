import nflreadpy as nfl

from ingestion.ducklake import get_connection


def main() -> None:
    season = nfl.get_current_season()
    draft_picks = nfl.load_draft_picks(seasons=season)

    with get_connection() as conn:
        conn.register('draft_picks', draft_picks)
        conn.sql(f'DELETE FROM lake.raw.nfl_draft_picks WHERE season = {season}')
        conn.sql("""
            INSERT INTO lake.raw.nfl_draft_picks BY NAME
            SELECT *
            FROM draft_picks
        """)

        result = conn.sql(
            f'SELECT COUNT(*) FROM lake.raw.nfl_draft_picks WHERE season = {season}'
        ).fetchone()
        if result is None:
            raise RuntimeError('COUNT(*) returned no rows')
        print(f'Loaded {result[0]} rows into lake.raw.nfl_draft_picks')


if __name__ == '__main__':
    main()
