import subprocess
from pathlib import Path

from dagster import asset, AssetExecutionContext, AssetKey

REPO_ROOT = Path(__file__).resolve().parents[2]  # orchestration/assets → repo root


@asset(
    key_prefix=['dbt'],
    group_name='transform',
    deps=[
        AssetKey(['raw', 'nfl_teams']),
        AssetKey(['raw', 'nfl_players']),
        AssetKey(['raw', 'nfl_player_stats']),
        AssetKey(['raw', 'nfl_team_stats']),
        AssetKey(['raw', 'nfl_schedules']),
        AssetKey(['raw', 'nfl_rosters']),
        AssetKey(['raw', 'nfl_draft_picks']),
    ],
    description='dbt build: silver stg_* + gold dim_*/fact_*',
)
def dbt_build(context: AssetExecutionContext) -> None:
    cmd = [
        'uv',
        'run',
        'dbt',
        'build',
        '--project-dir',
        'statline_dbt',
        '--profiles-dir',
        'statline_dbt',
    ]
    context.log.info('Running: %s (cwd=%s)', ' '.join(cmd), REPO_ROOT)
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,  # critical for DuckLake relative paths
        capture_output=True,
        text=True,
        check=False,
    )
    context.log.info(result.stdout)
    if result.returncode != 0:
        context.log.error(result.stderr)
        raise RuntimeError(f'dbt build failed with code {result.returncode}')
