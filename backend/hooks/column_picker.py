import os
import pandas as pd
from fastapi import APIRouter

RAW_PATH = "./local_data/raw"

router = APIRouter()

@router.get("/columns/{dataset_id}")
def get_column_names(dataset_id: str):
    csv_path = os.path.join(RAW_PATH, f"{dataset_id}.csv")
    if not os.path.exists(csv_path):
        return {"status": "error", "message": "Dataset file not found"}

    try:
        df = pd.read_csv(csv_path)
        if len(df.columns) == 1:
            df = pd.read_csv(csv_path, sep=';')
        return {"status": "success", "columns": df.columns.tolist()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
