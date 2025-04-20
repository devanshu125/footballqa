import glob
import duckdb

connector = duckdb.connect("../db_folder/footballqa.duckdb")

all_paths = list(glob.glob("../csv_data_folder/*.csv"))
for req_path in all_paths:
    # get the file name
    req_file_name = req_path.split("/")[-1].split(".")[0]
    # we don't need game_lineups as we are taking the cleaned version
    if req_file_name == "game_lineups":
        continue

    if req_file_name not in ["game_lineups_cleaned", "appearances", "player_valuations", "game_events"]:
        print(req_file_name, req_path)
        connector.execute(f"""
            CREATE TABLE {req_file_name} AS 
            SELECT * FROM read_csv_auto('{req_path}');
        """)
    else:
        # use the split folder path
        print("Using split folder for", req_file_name)
        connector.execute(f"""
            CREATE TABLE {req_file_name} AS 
            SELECT * FROM read_csv_auto('../csv_data_folder/split/{req_file_name}/*.csv');
        """)