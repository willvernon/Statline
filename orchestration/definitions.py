from dagster import (
    Definitions,
    AssetSelection,
    DefaultScheduleStatus,
    ScheduleDefinition,
    define_asset_job,
)
from dagster_dbt import DbtCliResource

# Catalog → absolute; DATA_PATH stays relative (matches DuckLake catalog string).
from orchestration.resources.paths import normalize_lake_env

normalize_lake_env()

from orchestration.assets.raw import raw_nfl
from orchestration.assets.dbt_project import statline_dbt_assets, DBT_PROJECT_DIR

nfl_weekly_job = define_asset_job(
    name="nfl_weekly_refresh",
    selection=AssetSelection.groups("bronze", "silver", "gold"),
)
nfl_weekly_schedule = ScheduleDefinition(
    name="nfl_weekly_schedule",
    job=nfl_weekly_job,
    cron_schedule="0 8 * * 2",
    execution_timezone="America/Indiana/Indianapolis",
    default_status=DefaultScheduleStatus.STOPPED,
)

defs = Definitions(
    assets=[
        raw_nfl,
        statline_dbt_assets,
    ],
    resources={
        "dbt": DbtCliResource(project_dir=DBT_PROJECT_DIR),
    },
    jobs=[nfl_weekly_job],
    schedules=[nfl_weekly_schedule],
)
