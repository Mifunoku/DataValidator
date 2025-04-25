import pandas as pd
import os, json
from uuid import uuid4

RAW_PATH = "./local_data/raw"
DB_PATH = "./local_data/db"
os.makedirs(DB_PATH, exist_ok=True)

def evaluate_local(dataset_id, product_column, category_column):
    csv_path = os.path.join(RAW_PATH, f"{dataset_id}.csv")
    print("Reading CSV:", csv_path)
    df = pd.read_csv(csv_path)
    if len(df.columns) == 1:
        df = pd.read_csv(csv_path, sep=';')
    if len(df.columns) == 1:
        raise Exception("CSV file accepts only ',' or ';' as separator")

    print("Using product column:", product_column)
    print("Using category column:", category_column)

    rows = []
    wrong = 0

    for i, row in df.iterrows():
        model_cat = row[category_column]
        actual = row[product_column]
        correct = model_cat == actual
        if not correct:
            wrong += 1

        rows.append({
            "id": i,
            "product_text": str(actual),
            "model_category": str(model_cat),
            "fixed_category": None,
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

    print(f"Evaluation complete for {dataset_id} with {len(rows)} rows")
