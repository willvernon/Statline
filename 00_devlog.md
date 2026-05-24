# Stateline Project DevLog

## 2026-05-24

### Project Scoped & Stack Decided

Long planning session focused on project direction before writing a single line of code.

#### Project: statline

A production-style NFL data pipeline for player and team game analytics. Built to feed personal sports projects and a Sports App without spending the majority of time on ETL every time fresh data is needed.

#### Stack decided:

Data Sources: nflreadpy, nflverse, Pro Football Reference
ETL: Databricks
Transformation: dbt (via Databricks connector)
Storage: Delta Lake (via Databricks)
Orchestration: Databricks Workflows
Dashboard: Streamlit + Sports App

#### Key decisions:

Switched from Snowflake to Databricks which was recommended by a senior DE, Free Edition available, lakehouse architecture is the better long-term bet.

_Star Schema_: two fact tables, three dimension tables

The grain of core _fact tables_ locked:

- one row per player per game (`fact_player_game`)
- one row per team per game (`fact_team_game`)

The _dimension tables_:

- `dim_player`
- `dim_team`
- `dim_game`

NFL only to start

- off-season means stable historical data,
- no chasing live updates until 2025 season begins

### The professional setup order:\*\*

1. **GitHub repo first** — everything lives here from day one. No exceptions.
2. **Project structure** — create your folder skeleton before writing any code. Commit it empty with `.gitkeep` files.
3. **Environment isolation** — never install packages globally. Use a virtual environment or conda env scoped to this project.
4. **Dependency management** — `requirements.txt` or `pyproject.toml` committed to the repo. Anyone should be able to clone and reproduce your environment exactly.
5. **Environment variables** — credentials and secrets go in a `.env` file immediately. `.env` goes in `.gitignore` immediately. Never commit credentials. Ever.
6. **Docker** — containerize early, not as an afterthought. A `docker-compose.yml` that spins up your local environment means it runs the same on every machine.
7. **dbt project init** — run `dbt init` inside your project folder, not as a standalone repo.
8. **Branch strategy** — `main` is always clean and working. All development happens on feature branches. Merge via pull request even when you're solo. This is what professional repos look like.
9. **Commit messages** — write them like documentation. "add player stats ingestion script" not "stuff" or "update."

**The `.gitignore` needs these from day one:**

```
.env
__pycache__/
*.pyc
.venv/
target/
dbt_packages/
logs/
```

Set up the repo and folder structure first. What does your current folder structure look like?

#### Next Up:

Set up GitHub repo and folder structure
Get Databricks Community Edition running
Explore nflreadpy — pull raw data and understand what's actually in it before writing ingestion scripts

---
