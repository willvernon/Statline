# statline

**Current scope:** Historical NFL player stats and roster data (2000–2024)
**Planned:** Live game ingestion when the 2025 season begins

---

## Objective

Building a data pipeline to support sports modeling and analytics. I have many hobby projects during the NFL season that model and analyze different situations. The problem I run into is that I'm very busy and the data sources I use require a full ETL every time I need fresh data, leaving little time for actual analysis. I also built a Sports App that needed a better way to handle historical data. Statline solves this by building a production-style automated pipeline that handles ingestion, transformation, and storage so the data is always ready.

## Stack

**Data Sources:** nflreadpy · Pro Football Reference · nflverse · additional open source sources

**ETL:** Databricks · dbt (via Databricks connector)

**Storage:** Delta Lake (via Databricks)

**Orchestration:** Databricks Workflows

**Dashboard:** Streamlit · Sports App
