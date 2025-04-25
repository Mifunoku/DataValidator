from fastapi import APIRouter, Query
from functions.evaluate.app import evaluate_local
from google.cloud import storage
import pandas as pd
import io

router = APIRouter()

# GCS client
storage_client = storage.Client()
RAW_BUCKET = "ds-raw-files"

@router.get("/columns/{dataset_id}")
def get_column_names(dataset_id: str):
    try:
        bucket = storage_client.bucket(RAW_BUCKET)
        blob = bucket.blob(f"raw/{dataset_id}.csv")

        if not blob.exists():
            return {"status": "error", "message": "Dataset file not found"}

        content = blob.download_as_bytes()

        try:
            df = pd.read_csv(io.BytesIO(content))
            if len(df) <= 1:
                df = pd.read_csv(io.BytesIO(content), sep=';')
        except Exception:
            return {"status": "error", "message": "Failed to read CSV file"}

        return {"status": "success", "columns": df.columns.tolist()}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/evaluate/{dataset_id}")
def evaluate_with_columns(dataset_id: str, product_column: str = Query(...), category_column: str = Query(...)):
    try:
        evaluate_local(dataset_id, product_column, category_column)
        return {"status": "success", "message": f"Evaluated {dataset_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
