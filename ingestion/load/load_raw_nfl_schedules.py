import nflreadpy as nfl

from ingestion.ducklake import get_connection


def main() -> None:
    schedules = nfl.load_schedules()

    with get_connection() as conn:
        conn.register('schedules', schedules)
        conn.sql('DELETE FROM lake.raw.nfl_schedules')
        conn.sql(
            """
                INSERT INTO lake.raw.nfl_schedules
                SELECT *
                FROM schedules
                """
        )
        result = conn.sql('SELECT COUNT(*) FROM lake.raw.nfl_schedules').fetchone()
        if result is None:
            raise RuntimeError('COUNT(*) returned no rows')
        print(f'Loaded {result[0]} rows into lake.raw.nfl_schedules')


if __name__ == '__main__':
    main()
