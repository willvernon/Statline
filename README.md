# statline

Local sports data lakehouse. Right now that means non-live NFL (box scores, schedules, rosters, draft) landed in DuckLake, cleaned in dbt, orchestrated in Dagster, and served as a star schema.

The graph is wired and there is a weekly Dagster job. It is not an always-on scheduler, and a fresh clone does not backfill 2000-2024 on its own.

**Built:** bronze ingest, silver staging, gold marts, local Dagster assets + `nfl_weekly_refresh`  
**Not built:** live game feeds, multi-sport, one-command 2000-2024 backfill

## Why this exists

I burn a lot of time re-pulling and re-shaping public NFL data every week in season for hobby models, analysis, and a sports app. I want that work sitting in a pipeline so the data is already clean and queryable when I need it.

## Stack (and the pivot)

Originally scoped for Databricks + Unity Catalog + Delta. The data is one sport and about 25 seasons of box scores. Distributed compute was solving a problem I don't have, so I pivoted to fully local.

| Piece         | Choice                              |
| ------------- | ----------------------------------- |
| Extract       | Python + `nflreadpy`                |
| Load          | Python → DuckLake (`lake.raw`)      |
| Storage       | DuckLake (SQL catalog + Parquet)    |
| Transform     | dbt + `dbt-duckdb`                  |
| Orchestration | Dagster (local job + schedule)      |
| Env           | `uv` + `pyproject.toml` / `uv.lock` |

## Pipeline

```
nflreadpy → Python load → lake.raw (bronze)
                       → dbt stg_* (silver)
                       → dbt dim_* / fact_* (gold)
                       → notebooks / sports app (non-live)

         Dagster: bronze → silver → gold
         job: nfl_weekly_refresh (manual launch or the Tuesday schedule)
```

| Layer  | Schema / objects                   | Owner                                             |
| ------ | ---------------------------------- | ------------------------------------------------- |
| Bronze | `lake.raw.nfl_*`                   | Python loaders. Source-shaped, no star renames.   |
| Silver | `lake.main_staging.stg_*`          | dbt views. Clean, rename, key filters.            |
| Gold   | `lake.main_marts.dim_*` / `fact_*` | dbt tables. Star schema for app + shared metrics. |

dbt prefixes custom schemas with the target schema (`main`), so you see `main_staging` / `main_marts` instead of bare `staging` / `marts`. Same idea as `raw`.

### Asset graph (Dagster)

Medallion groups in the local UI: bronze raw loaders, silver staging, gold marts.

![Dagster asset graph: bronze, silver, gold](docs/images/dagster-asset-graph.svg)

## Data model (gold)

**Facts**

- `fact_player_game`: one row per player per game (wide box score)
- `fact_team_game`: one row per team per game

**Dims**

- `dim_player`: natural key `gsis_id` (`player_id` on facts maps here)
- `dim_team`: natural key `team_abbr`
- `dim_game`: natural key `game_id`

Rosters and draft picks live in silver only for now.

## Repo layout

```
ingestion/              # DuckLake connect + raw loaders
  load/                 # load_raw_nfl_*.py
  schemas/              # DDL for lake.raw
orchestration/          # Dagster definitions + assets
  assets/               # raw multi-asset, dagster-dbt
  resources/            # lake path normalization
scripts/                # ingestion-runner.py
statline_dbt/           # dbt project (staging + marts)
docs/                   # design notes + graphs
  multi-sport-data.md   # how more leagues would land (no code yet)
lake/                   # local catalog + parquet (gitignored)
notebooks/              # exploration (not the pipeline)
```

## Setup

**Requirements:** Python ≥ 3.13, [uv](https://docs.astral.sh/uv/)

```bash
git clone <repo>
cd Statline
uv sync
cp .env.example .env
```

`.env` (from `.env.example`):

```bash
LAKE_CATALOG_PATH=lake/metadata.ducklake
LAKE_DATA_PATH=lake/data
```

Paths are **relative to the repo root**. Always run from the repo root, not from `statline_dbt/`. The catalog stores the data path as `lake/data/`.

Python loaders read `.env` on their own. **dbt CLI does not**, and `dagster dev` does not pick up `DAGSTER_HOME` from `.env` either. Export what those two need in the session (see below).

## Run

### Initialize empty lake (first time)

```bash
uv run python -m ingestion.ducklake
```

### Load raw (bronze)

```bash
# current season (nflreadpy.get_current_season() on season-scoped tables)
uv run python scripts/ingestion-runner.py

# one season
uv run python scripts/ingestion-runner.py 2024

# or one table (current-season default; no CLI year on the individual loaders)
uv run python ingestion/load/load_raw_nfl_teams.py
```

A year on the runner reloads that season for stats, schedules, rosters, and draft. Teams and players are full snapshots. There is no loop for 2000-2024, so a fresh clone does not reproduce the full history in one command.

### Transform (silver + gold)

Export lake paths first, then:

```bash
export LAKE_CATALOG_PATH=lake/metadata.ducklake
export LAKE_DATA_PATH=lake/data
# or: set -a && source .env && set +a

uv run dbt debug --project-dir statline_dbt --profiles-dir statline_dbt
uv run dbt build --project-dir statline_dbt --profiles-dir statline_dbt
```

**Fish:** `set -x LAKE_CATALOG_PATH lake/metadata.ducklake` and `set -x LAKE_DATA_PATH lake/data`.

`statline_dbt/profiles.yml` uses `threads: 1`. Parallel dbt materializations were flaky against local DuckLake. Single-thread is the path that actually works for a demo.

### Orchestrate (Dagster, local)

From **repo root**. Lake paths come from `.env` when the code location loads. `DAGSTER_HOME` still has to be an absolute path in the shell, or you get a fresh `.tmp_dagster_home_*` every start.

```bash
mkdir -p .dagster_home
export DAGSTER_HOME="$PWD/.dagster_home"
uv run dagster dev -m orchestration.definitions
```

**Fish:** `mkdir -p .dagster_home; set -x DAGSTER_HOME (pwd)/.dagster_home`

Open http://localhost:3000.

- Materialize bronze (`raw/*`), then silver/gold, or launch the `nfl_weekly_refresh` job (same graph).
- Schedule `nfl_weekly_schedule` is in `orchestration/definitions.py` (Tue 8am Indianapolis). It starts Stopped. Enable it in Automation if you want the Tuesday tick. Nothing fires unless this process is running.
- Bronze assets wrap the existing `load_raw_nfl_*.py` loaders (season config on seasonal tables).
- Silver/gold come from `dagster-dbt` and the dbt manifest. Groups are `bronze` / `silver` / `gold`.
- dagster-dbt runs with cwd = `statline_dbt/`. Orchestration makes lake paths absolute and dbt sets `override_data_path` so parquet still lands in the repo `lake/` tree.

### Query

Attach the same lake (DuckDB CLI, notebook, or app):

- Exploration / flexible analysis: `main_staging.stg_*`
- App + official metrics: `main_marts.dim_*` / `fact_*`

## Development notes

- **uv only** for Python deps. No global `pip install`.
- **Feature branches + PRs** even solo. `main` stays merge-only.
- **Never commit** `.env`, `lake/`, `*.duckdb`, dbt `target/`, `.dagster_home/`
- Running notes live in `devlog/` (local, gitignored)
- Working list: `todo.md` (local, gitignored)

## Status

| Phase                       | State                                 |
| --------------------------- | ------------------------------------- |
| Setup + DuckLake            | Done                                  |
| Bronze ingest (`nfl_*` raw) | Done                                  |
| dbt silver (`stg_*`)        | Done                                  |
| dbt gold (star marts)       | Done                                  |
| Dagster assets + weekly job | Done                                  |
| One-command historical load | Next (runner takes one season today)  |
| Live feeds / multi-sport    | Next. Map: `docs/multi-sport-data.md` |
