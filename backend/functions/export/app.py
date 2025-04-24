import os, json, csv

DB_PATH = "./local_data/db"
EXPORT_PATH = "./local_data/results"
os.makedirs(EXPORT_PATH, exist_ok=True)

def export_local(dataset_id):
    with open(os.path.join(DB_PATH, f"{dataset_id}_rows.json")) as f:
        rows = json.load(f)

    out_path = os.path.join(EXPORT_PATH, f"{dataset_id}.csv")
    with open(out_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["product_text", "model_category", "fixed_category"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Exported corrected CSV to {out_path}")
    return out_path
