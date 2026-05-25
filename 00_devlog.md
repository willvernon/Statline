# Stateline Project DevLog

## *2026-05-24*

### Project scoped & stack decided
> Long planning session before writing any code.

- Named project **statline** — production-style NFL pipeline for personal analytics and Sports App
- Locked star schema grain and table names
- Explored nflreadpy / nflverse / PFR as sources; nflreadpy primary for extract

**Stack decided:**
- Extract: Python (nflreadpy) · Load: Python → Databricks · Storage: Delta Lake (Unity Catalog)
- Transform: dbt-databricks · Orchestration: Databricks Workflows or Airflow · Dashboard: Streamlit

**Key decisions:**
- `fact_player_game` stays wide — all box-score columns; position views in dbt later, not separate core facts
- `dim_player` filtered to columns I care about
- NFL only to start; historical 2000–2024; no live ingestion until 2025 season

### Stack pivot to Databricks
> Moved off DuckDB/Snowflake — Databricks access available; Delta + Unity Catalog better fit for portfolio pipeline.

- Updated stack across README, AGENTS.md, devlog, pyproject.toml
- Removed dbt-duckdb / dbt-snowflake / duckdb; added dbt-databricks
- Pinned pandas 2.2.x and dbt-core 1.11.8 for adapter compatibility

**Key decisions:**
- Python ingestion loads directly to Databricks; dbt owns all transforms
- Docker demoted to optional (Airflow local only)

---

## :Todo
1. - [x] Setup — repo, structure, tools, credentials
2. - [x] Data sourcing — identify and explore raw data in notebooks
3. - [ ] Schema design — star schema diagram before writing any SQL in dbdiagram
4. - [ ] Raw ingestion — Python scripts load raw data
5. - [ ] Staging models — dbt cleans and types raw data
6. - [ ] Mart models — dbt builds fact and dimension tables
7. - [ ] Data quality — dbt tests on every model
8. - [ ] Validation — query marts, verify correctness manually
9. - [ ] Orchestration — Databricks Workflows or Airflow
10. - [ ] CI/CD — GitHub Actions runs dbt tests on push
11. - [ ] Dashboard — Streamlit layer on top of marts
12. - [ ] Documentation — architecture diagram, README, devlog

---
