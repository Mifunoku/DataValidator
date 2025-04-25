import pandas as pd
from google.cloud import firestore, storage
import os
import tempfile

RESULTS_BUCKET = "your-results-bucket-name"  # TODO: replace with your GCS bucket name

def export_local(dataset_id):
    db = firestore.Client()
    storage_client = storage.Client()

    rows_ref = db.collection('datasets').document(dataset_id).collection('rows')
    docs = rows_ref.stream()

    rows = [doc.to_dict() for doc in docs]

    if not rows:
        raise ValueError("No rows found to export.")

    df = pd.DataFrame(rows)

    # Save CSV to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
        df.to_csv(tmp_file.name, index=False)
        tmp_file_path = tmp_file.name

    # Upload to GCS results bucket
    bucket = storage_client.bucket(RESULTS_BUCKET)
    blob = bucket.blob(f"results/{dataset_id}_corrected.csv")
    blob.upload_from_filename(tmp_file_path)

    print(f"Exported corrected CSV for {dataset_id} to GCS bucket {RESULTS_BUCKET}")

    # Clean up temp file
    os.remove(tmp_file_path)
