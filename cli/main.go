package main

import (
	"database/sql"
	"flag"
	"fmt"
	"os"

	_ "github.com/duckdb/duckdb-go/v2"
)

var goldMarts = map[string]struct{}{
	"dim_game":         {},
	"dim_player":       {},
	"dim_team":         {},
	"fact_player_game": {},
	"fact_team_game":   {},
}

func main() {

	dataMart := flag.String("dataMart", "fact_player_game", "gold mart to export")
	dest := flag.String("dest", "", "parquet file (default: export/<mart>.parquet)")
	flag.Parse()

	if _, ok := goldMarts[*dataMart]; !ok {
		fmt.Fprintf(os.Stderr, "unknown mart %q\nallowed: dim_game dim_player dim_team fact_player_game fact_team_game\n", *dataMart)
		os.Exit(1)
	}

	db, err := sql.Open("duckdb", "")
	if err != nil {
		fmt.Println("DB Connection: Failed", err)
		return
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		fmt.Println("DB Connection: Failed", err)
		return
	}
	fmt.Println("DB Connection: Success")

	_, err = db.Exec("ATTACH 'ducklake:lake/metadata.ducklake' AS lake (DATA_PATH 'lake/data')")
	if err != nil {
		fmt.Println("ATTACH failed:", err)
		return
	}

	sqlToParquet := fmt.Sprintf(
		"COPY lake.main_marts.%s TO '%s' (FORMAT parquet)",
		*dataMart,
		*dest,
	)

	_, err = db.Exec(sqlToParquet)
	if err != nil {
		fmt.Println("Error with query:", err)
		return
	}
	fmt.Println("wrote", *dest)
}
