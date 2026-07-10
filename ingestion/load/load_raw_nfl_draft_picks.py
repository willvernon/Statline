import nflreadpy as nfl

from ingestion.ducklake import get_connection


def main() -> None:
    draft_picks = nfl.load_draft_picks()

    with get_connection() as conn:
        conn.register('draft_picks', draft_picks)
        conn.sql("""
            INSERT INTO lake.raw.nfl_draft_picks
            SELECT *
            FROM draft_picks
        """)

        result = conn.sql('SELECT COUNT(*) FROM lake.raw.nfl_draft_picks').fetchone()
        if result is None:
            raise RuntimeError('COUNT(*) returned no rows')
        print(f'Loaded {result[0]} rows into lake.raw_nfl_draft_picks')


if __name__ == '__main__':
    main()
