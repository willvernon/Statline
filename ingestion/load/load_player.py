import os
from dotenv import load_dotenv

import duckdb
import nflreadpy as nfl

load_dotenv()

player = nfl.load_players()

conn = duckdb.connect()
conn.sql(
    f"ATTACH 'ducklake:{os.environ['LAKE_CATALOG_PATH']}' AS lake "
    f"(DATA_PATH '{os.environ['LAKE_DATA_PATH']}')"
)

conn.register("player", player)
conn.sql(
    """
    INSERT INTO lake.raw.dim_player
    SELECT
        gsis_id,
        esb_id,
        nfl_id,
        pfr_id,
        pff_id,
        otc_id,
        espn_id,
        smart_id,
        display_name,
        common_first_name,
        first_name,
        last_name,
        short_name,
        football_name,
        suffix,
        birth_date,
        height,
        weight,
        headshot,
        college_name,
        college_conference,
        position_group,
        position,
        ngs_position_group,
        ngs_position,
        pff_position,
        jersey_number,
        rookie_season,
        last_season,
        latest_team,
        status,
        ngs_status,
        ngs_status_short_description,
        years_of_experience,
        pff_status,
        draft_year,
        draft_round,
        draft_pick,
        draft_team
    FROM player
    """
)
