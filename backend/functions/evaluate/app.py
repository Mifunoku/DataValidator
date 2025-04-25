import pandas as pd
from google.cloud import firestore, storage
from io import StringIO
import uuid

# Firestore client
db = firestore.Client()

# Storage client
storage_client = storage.Client()

# Raw bucket name
RAW_BUCKET = "ds-raw-files"  # <-- Make sure this is your real bucket name

def evaluate_local(dataset_id: str, product_column: str, category_column: str):
    # Get the blob from GCS
    bucket = storage_client.bucket(RAW_BUCKET)
    blob = bucket.blob(f"raw/{dataset_id}.csv")

    # Download CSV content as text
    contents = blob.download_as_text()

    # Parse CSV
    df = pd.read_csv(StringIO(contents))
    if len(df.columns) == 1:
        df = pd.read_csv(StringIO(contents), sep=';')

    if len(df.columns) == 1:
        raise ValueError("CSV file has only one column. Please check the file format.")

    # Evaluate rows
    rows = []
    correct = 0
    wrong = 0

    for idx, row in df.iterrows():
        product_text = row.get(product_column)
        model_category = row.get(category_column)

        if not isinstance(product_text, str) or not isinstance(model_category, str):
            continue

        if product_text.lower() in model_category.lower():
            correct += 1
        else:
            wrong += 1

        rows.append({
            "id": idx,
            "product_text": product_text,
            "model_category": model_category,
            "fixed_category": None
        })

    # Save rows to Firestore (batch)
    batch = db.batch()
    dataset_ref = db.collection("datasets").document(dataset_id)

    for row in rows:
        row_ref = dataset_ref.collection("rows").document(str(row["id"]))
        batch.set(row_ref, row)

    batch.commit()

    print(f"Saved {len(rows)} rows for dataset {dataset_id} to Firestore")

    # Save evaluation metrics
    total = correct + wrong
    accuracy = round(100 * correct / total, 2) if total > 0 else 0.0

    dataset_ref.set({
        "total": total,
        "correct_initial": correct,
        "wrong_initial": wrong,
        "accuracy_initial": accuracy
    }, merge=True)

    print(f"Metrics updated for {dataset_id}")
