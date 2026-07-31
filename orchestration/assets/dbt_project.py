from pathlib import Path
from typing import Any, Mapping

from dagster import AssetExecutionContext
from dagster_dbt import (
    DagsterDbtTranslator,
    DbtCliResource,
    DbtProject,
    dbt_assets,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_PROJECT_DIR = REPO_ROOT / 'statline_dbt'

dbt_project = DbtProject(project_dir=DBT_PROJECT_DIR)
dbt_project.prepare_if_dev()


class StatlineDbtTranslator(DagsterDbtTranslator):
    """Map dbt folders to medallion groups for the Dagster UI / lineage story."""

    def get_group_name(self, dbt_resource_props: Mapping[str, Any]) -> str | None:
        fqn = dbt_resource_props.get('fqn') or []
        if 'staging' in fqn:
            return 'silver'
        if 'marts' in fqn:
            return 'gold'
        return super().get_group_name(dbt_resource_props)


@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=StatlineDbtTranslator(),
)
def statline_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(['build'], context=context).stream()
