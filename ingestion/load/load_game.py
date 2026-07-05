import os

import duckdb
import nflreadpy as nfl
from dotenv import load_dotenv

load_dotenv()

game = nfl.load_schedules()


conn = duckdb.connect()
conn.sql(
    f"ATTACH 'ducklake:{os.environ['LAKE_CATALOG_PATH']}' AS lake "
    f"(DATA_PATH '{os.environ['LAKE_DATA_PATH']}')"
)

conn.register("game", game)
conn.sql(
    """
    INSERT INTO lake.raw.dim_game
    SELECT
        game_id,
        season::VARCHAR,
        week,
        game_type AS season_type,
        gameday AS game_date,
        home_team AS home_team_abbr,
        away_team AS away_team_abbr,
        stadium,
        location,
        roof AS roof_type,
        surface
    FROM game
    """
)
