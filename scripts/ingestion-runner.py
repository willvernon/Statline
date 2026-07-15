from ingestion.load.load_raw_nfl_draft_picks import main as load_draft_picks
from ingestion.load.load_raw_nfl_player_stats import main as load_player_stats
from ingestion.load.load_raw_nfl_players import main as load_players
from ingestion.load.load_raw_nfl_rosters import main as load_rosters
from ingestion.load.load_raw_nfl_schedules import main as load_schedules
from ingestion.load.load_raw_nfl_team_stats import main as load_team_stats
from ingestion.load.load_raw_nfl_teams import main as load_teams


def main() -> None:
    loaders = [
        load_draft_picks,
        load_player_stats,
        load_players,
        load_rosters,
        load_schedules,
        load_team_stats,
        load_teams,
    ]

    for loader in loaders:
        try:
            loader()
        except Exception as e:
            print(f'FAILED {loader.__module__}: {e}')


if __name__ == '__main__':
    main()
