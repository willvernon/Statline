# Multi-sport data: sources, pipelines, schema

Statline is one lake and one Dagster project. That should stay true when more sports show up. What should not stay true is one star that tries to hold passing yards and batting average in the same fact table.

This note is a map. No code changes.

NFL today is the template to copy, not the model to stretch. Bronze is source-shaped (`lake.raw.nfl_*`). Silver cleans it. Gold is a small NFL star for the app. Multi-sport means more extractors and more stars, not a wider `fact_player_game`.


## What "connect the data" means

Three jobs, not one.

1. Extract. Talk to a source and land tables.
2. Align. Same lake, same season key, same load pattern.
3. Model. Make tables a notebook or an app can query without knowing ESPN JSON.

A working team splits extract by sport and shares align. They only share the model where the grain is actually the same. Across these six leagues, it almost never is.


## How a working team actually pulls each sport

A product company buys Sportradar, Stats Perform, or SportsDataIO. Licensed, live, and a schema you do not control. Wrong first move for this repo.

The realistic path is the one NFL already uses. Community releases and public APIs, season-partitioned, written into `lake.raw`. Same loader shape as `load_raw_nfl_player_stats.py`:

```
fetch(season) → register frame → DELETE that season → INSERT BY NAME
```

That is the pipeline. Copy it. A shared helper can wait until the third sport.

Pick the best source per league. Standardize the landing pattern, not the client. An umbrella package that wraps all six is convenient and then becomes the outage.

| League | Use this | What lands | Catch |
| ------ | -------- | ---------- | ----- |
| NFL | `nflreadpy` (already) | teams, players, rosters, schedules, player/team week stats. PBP is sitting in nflverse if you want it. | Keep it. Do not wrap it in another library. |
| NBA | Season releases (`load_nba_*` / hoopR-style parquet) for history. `nba_api` for the current season if a release lags. | schedule, player box, team box, PBP, shots | stats.nba.com breaks without warning. Cache history. Do not scrape Basketball-Reference as primary. |
| MLB | MLB Stats API for people, schedule, box. Statcast via Savant / `pybaseball` for pitches. | two grains on purpose: game/box and pitch | Pitch data is large. It is not a column on a box-score table. |
| NHL | NHL `api-web` (free, official-ish) and/or fastRhockey-style loaders | schedule, box, PBP, shifts | Skater lines and goalie lines are different facts. Same trap as batter vs pitcher. |
| CFB | CollegeFootballData (cfbd) plus cfbfastR-data releases | games, rosters, PBP, drives, recruiting | API key. School and conference churn every offseason. FBS/FCS mixing in the schedule. |
| CBB | ESPN/NCAA via sportsdataverse `mbb` loaders | schedule, box, PBP | 350+ D1 teams, transfer portal, messy IDs. KenPom is not a free raw source. |

Secondary later, all sports: ESPN scoreboard as a complement, Sports-Reference / PFR as an ID crosswalk, an odds API if the app cares about lines. Not primary bronze. The README already flags PFR as a later NFL source. Same idea everywhere.

College and pro that share a ball do not share a table. CFB is not "NFL with extra teams." CBB is not NBA. The draft is the bridge. `nfl_draft_picks` already has `cfb_player_id`. That is the pattern: a map table, not a merged player dim.


## One pipeline or six?

One runtime. Six extractors.

Share DuckLake, the dbt project, the Dagster code location, env, and the season-partitioned load convention.

Split the Python client, raw DDL, staging models, gold facts, Dagster asset group, and refresh cadence.

If NFL ingest fails, NBA should still run. That is the test. A `raw_nfl`-style multi_asset per league is enough. Do not make six repos or six dbt projects.

Cadence is why this cannot be one linear job:

- NFL: weekly in season
- CFB: weekly, Saturday-heavy
- NBA / NHL: nightly
- MLB: nightly, plus a slower Statcast path
- CBB: nightly, brutal volume in February and March

dbt stays one project with folders and `+schema` per league (`staging/nba`, `marts/nba`, and so on). Tag-select by sport. Mesh is for when this is no longer a local lake.


## Why one star fails

The current gold model is a good NFL star: `dim_player`, `dim_team`, `dim_game`, `fact_player_game`, `fact_team_game`. Those facts are wide box scores. Correct for one sport and an app.

It breaks across sports for five concrete reasons.

**Grain.** NFL player-game. MLB batter-game, pitcher-game, and pitch. NHL skater vs goalie. NBA player-game vs lineup stint. One `fact_player_game` lies about at least three of those.

**Measures.** `passing_yards` and `batting_average` are not conformed facts. You get a sparse 400-column table or an EAV (`stat_name`, `stat_value`). DuckDB and dbt tests both hate the second. Analysts hate the first.

**Entities.** An NFL team is a franchise. A CFB team is a school. Conferences move. NBA/NHL/MLB franchises relocate and rename. College player-team is a time series because of the transfer portal. NFL rosters already are weekly. Do not pretend `dim_team.team_abbr` is universal.

**Time.** `week` is first-class in football and a lie in baseball. MLB has doubleheaders. CBB spans two calendar years. `season` is the only time key that mostly survives, and even that means different things (NFL 2024 vs CBB 2024-25).

**Identity.** NFL players already carry gsis, pfr, espn. Other sports add mlbam, nba `person_id`, cfbd, ncaa. There is no universal player key. Two-sport athletes are rare. College-to-pro is common and is a bridge, not a merge.

Star schema is a serving shape. Keep it. Build one small star per league. Not one star for every American men's sport.


## Options

**A. One mega-star.** `sport_code` on every dim, nullable measures on one fact. Looks unified. Querying it is worse than six tables. Skip.

**B. EAV facts.** One `fact_stat(entity, game, metric, value)`. Fine as an app cache for "plot this number." Unusable as the warehouse. Skip as the core.

**C. Data vault.** Hubs for person/team/game, satellites per source. Right for a company merging Sportradar, a league feed, and betting. Wrong for a local DuckLake. Skip.

**D. Sport-local stars plus a thin core.** Bronze and silver stay source-shaped and league-prefixed, like today. Gold is `marts_nfl`, `marts_nba`, each with its own dims and facts. A small `core` schema holds only what actually conforms: the sport list, calendar dates, and ID maps. This is the one to use.

**E. Event grain as the system of record.** Plays, pitches, shots, shifts in bronze/silver. Box-score stars built as aggregates. This is where serious modeling lives (EPA, RAPM, xG, Stuff+). Do it per sport when that sport's models need it. Do not block the app on it. NFL PBP should land as `raw.nfl_pbp` when you need it, not as extra columns on `fact_player_game`.


## Recommended shape

Keep naming: `lake.raw.{league}_{entity}`. Do not explode schemas until table count hurts. Forty bronze tables is fine.

**Core (shared, tiny)**

- `core.sport`. Codes `nfl`, `nba`, `mlb`, `nhl`, `cfb`, `cbb`, plus a pro/college level.
- `core.date`. Real calendar. Do not fake football weeks here.
- `core.player_id_map`. Columns `person_sk`, `sport`, `source`, `source_player_id`.
- `core.team_id_map`. Same idea.

These are bridges, not dims. Stand them up when a question needs them, draft and transfers being the usual ones. Do not merge Mahomes and Jokic into one player dim.

**Every league, bronze then silver**

- teams
- players, or derive from roster
- rosters, grain = player × team × season, and week where the sport has weeks
- games / schedules
- player box
- team box

**Extra facts the sport will demand**

- NFL / CFB: `pbp`. NFL already has `draft`.
- NBA / CBB: `pbp` or shots. Lineup stints if basketball modeling gets serious.
- MLB: `batter_game` and `pitcher_game` as separate boxes. `pitch` as its own table.
- NHL: `skater_game` and `goalie_game`. `shift` / `pbp` later.

Gold dims stay league-local. Prefer dbt `+schema` per league folder so NFL can keep calling it `dim_player` without a rename war.


## Direct answers

**Do they need their own pipelines?** Their own extractors, DDL, and models. Not their own lake, dbt project, or Dagster deployment.

**Best schema for all of this in the same pipeline?** Source-shaped bronze, league-prefixed silver, one star per league at gold, plus a tiny core of ID maps. Not one star. Not EAV.

**Is star wrong?** Star per sport is right for the app. One star for all six is the thing that feels off. That instinct is correct.

**What to add first, when the time comes.** Leave NFL gold alone. Add a sport by copying the NFL loader, not by generalizing NFL models. NBA is the closest grain to what you have. MLB is the best test of the design, because it will refuse to fit `fact_player_game`. CFB after NFL PBP exists, because the play model transfers and the draft bridge is already in the lake. CBB with NBA. Never mix college teams into pro team dims.
