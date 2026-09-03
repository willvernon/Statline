from ingestion.ducklake import get_connection


def main():
    with get_connection() as conn:
        conn.sql(
            f"COPY lake.main_marts.dim_game TO 'export/nfl/dim_game.parquet' (FORMAT parquet)"
        )
        conn.sql(
            f"COPY lake.main_marts.dim_player TO 'export/nfl/dim_player.parquet' (FORMAT parquet)"
        )
        conn.sql(
            f"COPY lake.main_marts.dim_team TO 'export/nfl/dim_team.parquet' (FORMAT parquet)"
        )
        conn.sql(
            f"COPY lake.main_marts.fact_player_game TO 'export/nfl/fact_player_game.parquet' (FORMAT parquet)"
        )
        conn.sql(
            f"COPY lake.main_marts.fact_team_game TO 'export/nfl/fact_team_game.parquet' (FORMAT parquet)"
        )


if __name__ == '__main__':
    main()
