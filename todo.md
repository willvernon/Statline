# R2 publish

After gold, the weekly Prefect flow overwrites the five marts on R2. Power BI imports the public URLs.

Already in place: gold marts in DuckLake, bucket `statline`, objects under `nfl/`, and `https://data.vernondev.com/nfl/<mart>.parquet`. The weekly flow stops at gold. There is no export task.

Marts: `dim_game`, `dim_player`, `dim_team`, `fact_player_game`, `fact_team_game`.

## Build

- [ ] Create an R2 API token scoped to the `statline` bucket (object read and write). Put the values in `.env`. Add the names only to `.env.example`: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `R2_ENDPOINT`.
- [ ] Add an export task downstream of the five gold models. `COPY` each mart to one parquet file, then PUT it to `nfl/<mart>.parquet` with `Cache-Control: no-cache`.
- [ ] Call that task at the end of `nfl_weekly_refresh` in `orchestration/weekly.py`.
- [ ] Run the flow once. Confirm `https://data.vernondev.com/nfl/dim_team.parquet` still returns a parquet file.
- [ ] In Power BI Desktop, one query per URL: `Binary.Buffer(Web.Contents(...))` then `Parquet.Document`. Anonymous auth. Relate `player_id` → `dim_player.gsis_id`, `team_abbr` → `dim_team.team_abbr`, `game_id` → `dim_game.game_id`.
- [ ] Publish the report. Schedule refresh for 9:00am Tuesday, after the 8:00am Prefect schedule. `python -m orchestration.weekly --serve` has to be running.

## Later

- [ ] CLI `-all`: write every mart into `export/`. Local copy only. It does not upload.
- [ ] After the five uploads succeed, the weekly flow calls the Power BI refresh API instead of relying on the 9:00am clock.

## Leave alone

- Do not enable Workers Paid, R2 Data Catalog, or any other billed Cloudflare product for this.
- Do not point Power BI at `lake/data`.
- Do not put a presigned URL in the report.
