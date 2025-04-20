import duckdb

# Connect to your database
con = duckdb.connect("../db_folder/footballqa.duckdb")

# Rename the table
con.execute("ALTER TABLE game_lineups_cleaned RENAME TO game_lineups")

# Verify the change
con.execute("SELECT * FROM game_lineups LIMIT 5").fetchall()

tables = con.execute("SHOW TABLES").fetchall()
print(tables)