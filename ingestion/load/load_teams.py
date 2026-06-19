import os
from dotenv import load_dotenv

import duckdb
import nflreadpy as nfl

load_dotenv()

teams = nfl.load_teams()

conn = duckdb.connect()
conn.sql(
    f"ATTACH 'ducklake:{os.environ['LAKE_CATALOG_PATH']}' AS lake "
    f"(DATA_PATH '{os.environ['LAKE_DATA_PATH']}')"
)

conn.register("teams", teams)
conn.sql(
    """
    INSERT INTO lake.raw.dim_teams
    SELECT team_id,team_nick, team_abbr, team_conf , team_division , team_color , team_color2 , team_color3 , team_color4 , team_logo_wikipedia , team_logo_espn , team_wordmark , team_conference_logo , team_league_logo , team_logo_squared 
    FROM teams
"""
)
