package main

import (
	"database/sql"
	"flag" // needed because you call flag.String / flag.Parse
	"fmt"

	_ "github.com/duckdb/duckdb-go/v2"
)

// Want to build a cli that the user can use flags
// to select data marts to download their parquet
func main() {
	// current_season := time.Now().Year()

	// flag.String registers the flag and returns *string.
	// nothing is read from the command line until Parse().
	dataMart := flag.String("dataMart", "fact_player_game", "Gold layer data mart to download")
	dest := flag.String("dest", "~/Downloads/", "Download location of parquet")
	flag.Parse()

	// after Parse, dereference: *data_mart and *dest are the actual strings.

	// in-memory DuckDB. catalog path does NOT go in Open.
	// ATTACH is SQL you Exec — there is no sql.Attach.
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

	// ATTACH to Lake. run from repo root so lake/data resolves.
	_, err = db.Exec("ATTACH 'ducklake:lake/metadata.ducklake' AS lake (DATA_PATH 'lake/data')")
	if err != nil {
		fmt.Println("ATTACH failed:", err)
		return
	}

	// COPY writes a file → Exec, not Query.
	// table must be lake.main_marts.<name>
	// dest must be a quoted .parquet *file*, not a directory, and ~ is not expanded by Go.
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
