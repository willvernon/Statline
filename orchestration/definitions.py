from dagster import Definitions
from dagster_dbt import DbtCliResource

# Catalog → absolute; DATA_PATH stays relative (matches DuckLake catalog string).
from orchestration.resources.paths import normalize_lake_env

normalize_lake_env()

from orchestration.assets.raw import raw_nfl
from orchestration.assets.dbt_project import statline_dbt_assets, DBT_PROJECT_DIR

defs = Definitions(
    assets=[
        raw_nfl,
        statline_dbt_assets,
    ],
    resources={
        'dbt': DbtCliResource(project_dir=DBT_PROJECT_DIR),
    },
)
