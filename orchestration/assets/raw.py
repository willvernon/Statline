from dagster import multi_asset, AssetOut, AssetExecutionContext, Config, Output

from ingestion.load.load_raw_nfl_teams import main as load_teams
from ingestion.load.load_raw_nfl_players import main as load_players
from ingestion.load.load_raw_nfl_player_stats import main as load_player_stats
from ingestion.load.load_raw_nfl_team_stats import main as load_team_stats
from ingestion.load.load_raw_nfl_schedules import main as load_schedules
from ingestion.load.load_raw_nfl_rosters import main as load_rosters
from ingestion.load.load_raw_nfl_draft_picks import main as load_draft_picks


class SeasonConfig(Config):
    season: int | None = None


@multi_asset(
    outs={
        'nfl_teams': AssetOut(key_prefix=['raw'], group_name='bronze'),
        'nfl_players': AssetOut(key_prefix=['raw'], group_name='bronze'),
        'nfl_player_stats': AssetOut(key_prefix=['raw'], group_name='bronze'),
        'nfl_schedules': AssetOut(key_prefix=['raw'], group_name='bronze'),
        'nfl_rosters': AssetOut(key_prefix=['raw'], group_name='bronze'),
        'nfl_team_stats': AssetOut(key_prefix=['raw'], group_name='bronze'),
        'nfl_draft_picks': AssetOut(key_prefix=['raw'], group_name='bronze'),
    },
    can_subset=True,
)
def raw_nfl(context: AssetExecutionContext, config: SeasonConfig):
    selected = context.selected_output_names

    if 'nfl_teams' in selected:
        load_teams()
        yield Output(None, output_name='nfl_teams')

    if 'nfl_players' in selected:
        load_players()
        yield Output(None, output_name='nfl_players')

    if 'nfl_player_stats' in selected:
        load_player_stats(config.season)
        yield Output(None, output_name='nfl_player_stats')

    if 'nfl_team_stats' in selected:
        load_team_stats(config.season)
        yield Output(None, output_name='nfl_team_stats')

    if 'nfl_schedules' in selected:
        load_schedules(config.season)
        yield Output(None, output_name='nfl_schedules')

    if 'nfl_rosters' in selected:
        load_rosters(config.season)
        yield Output(None, output_name='nfl_rosters')

    if 'nfl_draft_picks' in selected:
        load_draft_picks(config.season)
        yield Output(None, output_name='nfl_draft_picks')
