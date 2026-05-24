# Stateline Project DevLog

## 2026-05-24

### Project Scoped & Stack Decided

Long planning session focused on project direction before writing a single line of code.

#### Project: statline

A production-style NFL data pipeline for player and team game analytics. Built to feed personal sports projects and a Sports App without spending the majority of time on ETL every time fresh data is needed.

#### Tool Stack:
Data Sources:   nflreadpy, nflverse, Pro Football Reference
Extract/Load:   Python
Transform:      dbt (DuckDB adapter locally, Snowflake adapter when available)
Storage:        DuckDB (local) → Snowflake (when student account approved)
Orchestration:  Airflow (Docker)
Dashboard:      Streamlit + Sports App


#### Schema
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

## :Todo
1. - [x] Setup — repo, structure, tools, credentials
2. - [ ] Data sourcing — identify and explore raw data in notebooks
3. - [ ] Schema design — star schema diagram before writing any SQL in dbdiagram
4. - [ ] Raw ingestion — Python scripts load raw data
5. - [ ] Staging models — dbt cleans and types raw data
6. - [ ] Mart models — dbt builds fact and dimension tables
7. - [ ] Data quality — dbt tests on every model
8. - [ ] Validation — query marts, verify correctness manually
9. - [ ] Orchestration — Airflow (Docker)
10. - [ ] CI/CD — GitHub Actions runs dbt tests on push
11. - [ ] Dashboard — Streamlit layer on top of marts
12. - [ ] Documentation — architecture diagram, README, devlog

---
