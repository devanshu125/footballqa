import pandas as pd
import glob
import os

def split_csv(input_file, output_dir, chunk_size=100_000):
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(input_file))[0]

    for i, chunk in enumerate(pd.read_csv(input_file, chunksize=chunk_size)):
        chunk_file = os.path.join(output_dir, f"{basename}_part{i+1}.csv")
        chunk.to_csv(chunk_file, index=False)
        print(f"✅ Saved: {chunk_file}")

# check all df shapes
all_paths = list(glob.glob("../csv_data_folder/*.csv"))
req_dict = {}
for req_path in all_paths:
    req_name = req_path.split("/")[-1].split(".")[0]
    # we need to take cleaned game_lineups file
    if req_name == "game_lineups":
        continue

    df = pd.read_csv(req_path)
    print(f"{req_path}: {df.shape}")
    req_dict[req_path]  = df.shape[0]
    print("\n")

# get all keys > 200_000
to_split_data = {k:v for k, v in req_dict.items() if v > 200_000}

for req_path, req_size in to_split_data.items():
    # split the csv
    print(f"Splitting {req_path} with size {req_size}")
    output_dir = os.path.join("../csv_data_folder/split", os.path.basename(req_path.replace(".csv", "")))
    split_csv(req_path, output_dir)
