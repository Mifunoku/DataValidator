from fastapi import APIRouter, HTTPException
from api.models import DatasetMetrics, PatchRowRequest, DataRow
import json, os

router = APIRouter()
DATA_PATH = "./local_data/db"
os.makedirs(DATA_PATH, exist_ok=True)

@router.get("/dataset/{dataset_id}/metrics", response_model=DatasetMetrics)
def get_metrics(dataset_id: str):
    path = os.path.join(DATA_PATH, f"{dataset_id}_metrics.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Dataset not found")
    with open(path) as f:
        return json.load(f)

@router.patch("/rows/{dataset_id}/{row_id}")
def patch_row(dataset_id: str, row_id: int, body: PatchRowRequest):
    path = os.path.join(DATA_PATH, f"{dataset_id}_rows.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    with open(path) as f:
        data = json.load(f)

    if row_id >= len(data):
        raise HTTPException(status_code=404, detail="Row ID not found")

    data[row_id]["fixed_category"] = body.fixed_category

    with open(path, "w") as f:
        json.dump(data, f)

    return {"status": "ok"}
