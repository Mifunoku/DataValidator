from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from api.models import DatasetMetrics, PatchRowRequest, DataRow
import json, os
from functions.export.app import export_local

router = APIRouter()
DATA_PATH = "./local_data/db"
os.makedirs(DATA_PATH, exist_ok=True)


@router.post("/export/{dataset_id}")
def trigger_export(dataset_id: str):
    try:
        export_local(dataset_id)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/export/{dataset_id}")
def download_export(dataset_id: str):
    path = f"./local_data/results/{dataset_id}_corrected.csv"
    if not os.path.exists(path):
        return {"status": "error", "message": "Export file not found"}
    return FileResponse(path, media_type="text/csv", filename=f"{dataset_id}_corrected.csv")

@router.get("/dataset/{dataset_id}/rows")
def get_rows(dataset_id: str):
    path = os.path.join(DATA_PATH, f"{dataset_id}_rows.json")
    if not os.path.exists(path):
        return {"status": "error", "message": "Dataset not found"}
    with open(path) as f:
        return json.load(f)  # this returns a list of rows


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
