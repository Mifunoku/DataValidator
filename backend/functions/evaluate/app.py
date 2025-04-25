import pandas as pd
from google.cloud import firestore
import uuid


def evaluate_local(dataset_id, product_column: str, category_column: str):
    db = firestore.Client()

    # Path for raw uploads in GCS (adjust if needed)
    raw_bucket_name = "your-raw-bucket-name"  # TODO: replace with your GCS raw bucket name

    from google.cloud import storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(raw_bucket_name)
    blob = bucket.blob(f"raw/{dataset_id}.csv")

    # Download raw CSV content
    contents = blob.download_as_text()
    df = pd.read_csv(pd.compat.StringIO(contents), sep=';')

    # Build rows
    rows = []
    correct = 0
    wrong = 0

    for idx, row in df.iterrows():
        product_text = row.get(product_column)
        model_category = row.get(category_column)

        if not isinstance(product_text, str) or not isinstance(model_category, str):
            continue

        correct_prediction = (product_text.lower() in model_category.lower())
        if correct_prediction:
            correct += 1
        else:
            wrong += 1

        rows.append({
            "id": idx,
            "product_text": product_text,
            "model_category": model_category,
            "fixed_category": None
        })

    # Save parsed rows into Firestore
    batch = db.batch()
    dataset_ref = db.collection("datasets").document(dataset_id)

    for row in rows:
        row_ref = dataset_ref.collection("rows").document(str(row["id"]))
        batch.set(row_ref, row)

    batch.commit()

    print(f"Saved {len(rows)} rows for dataset {dataset_id} to Firestore")

    # Save initial evaluation metrics into Firestore
    dataset_ref.set({
        "total": correct + wrong,
        "correct_initial": correct,
        "wrong_initial": wrong,
        "accuracy_initial": round(100 * correct / (correct + wrong), 2) if (correct + wrong) else 0.0
    }, merge=True)

    print(f"Metrics updated for {dataset_id}")