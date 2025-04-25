# --- functions/export/app.py ---
import os
import json
import pandas as pd

DB_PATH = "./local_data/db"
RESULTS_PATH = "./local_data/results"
os.makedirs(RESULTS_PATH, exist_ok=True)

def export_local(dataset_id):
    print("Exporting dataset:", dataset_id)
    rows_path = os.path.join(DB_PATH, f"{dataset_id}_rows.json")
    if not os.path.exists(rows_path):
        raise FileNotFoundError("Rows file not found")
    print("opening dataset:", dataset_id)
    with open(rows_path) as f:
        rows = json.load(f)

    print("Exporting dataset:", dataset_id)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RESULTS_PATH, f"{dataset_id}_corrected.csv"), index=False)
    print(f"Exported corrected CSV for {dataset_id}")
