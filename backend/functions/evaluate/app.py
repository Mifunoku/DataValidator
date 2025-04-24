import pandas as pd
import os, json
from uuid import uuid4

RAW_PATH = "./local_data/raw"
DB_PATH = "./local_data/db"
os.makedirs(DB_PATH, exist_ok=True)

def evaluate_local(dataset_id):
    csv_path = os.path.join(RAW_PATH, f"{dataset_id}.csv")
    df = pd.read_csv(csv_path)

    rows = []
    wrong = 0
    for i, row in df.iterrows():
        fixed_category = None
        if row["model_category"] != row.get("product_category", row["model_category"]):
            wrong += 1
        rows.append({
            "id": i,
            "product_text": row["product_text"],
            "model_category": row["model_category"],
            "fixed_category": fixed_category,
        })

    metrics = {
        "total": len(df),
        "wrong_initial": wrong,
        "accuracy_initial": round(100 * (1 - wrong / len(df)), 2),
        "wrong_current": wrong,
        "accuracy_current": round(100 * (1 - wrong / len(df)), 2),
        "download_url": None,
    }

    with open(os.path.join(DB_PATH, f"{dataset_id}_rows.json"), "w") as f:
        json.dump(rows, f)

    with open(os.path.join(DB_PATH, f"{dataset_id}_metrics.json"), "w") as f:
        json.dump(metrics, f)

    print(f"Processed dataset {dataset_id} with {len(rows)} rows")

