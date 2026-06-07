# %%
import nflreadpy as nfl

# %%
p_stats = nfl.load_player_stats(seasons=[2025])
teams = nfl.load_teams()

# %%
print(teams)
