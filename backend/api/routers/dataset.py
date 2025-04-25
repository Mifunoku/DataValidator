from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.models import DatasetMetrics, PatchRowRequest
from google.cloud import firestore, storage
from functions.export.app import export_local
import io

router = APIRouter()

# Firestore client
db = firestore.Client()

# GCS client
storage_client = storage.Client()
RESULTS_BUCKET = "ds-results-files"

@router.post("/export/{dataset_id}")
def trigger_export(dataset_id: str):
    try:
        export_local(dataset_id)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/export/{dataset_id}")
def download_export(dataset_id: str):
    bucket = storage_client.bucket(RESULTS_BUCKET)
    blob = bucket.blob(f"results/{dataset_id}_corrected.csv")

    if not blob.exists():
        return {"status": "error", "message": "Export file not found"}

    stream = io.BytesIO()
    blob.download_to_file(stream)
    stream.seek(0)

    return StreamingResponse(stream, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={dataset_id}_corrected.csv"
    })

@router.get("/dataset/{dataset_id}/rows")
def get_rows(dataset_id: str):
    rows_ref = db.collection("datasets").document(dataset_id).collection("rows")
    docs = rows_ref.stream()
    return [doc.to_dict() for doc in docs]


@router.get("/dataset/{dataset_id}/metrics", response_model=DatasetMetrics)
def get_metrics(dataset_id: str):
    doc = db.collection("datasets").document(dataset_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Dataset not found")

    data = doc.to_dict()

    try:
        return DatasetMetrics(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid metrics data: {str(e)}")

@router.patch("/rows/{dataset_id}/{row_id}")
def patch_row(dataset_id: str, row_id: int, body: PatchRowRequest):
    row_ref = db.collection("datasets").document(dataset_id).collection("rows").document(str(row_id))

    if not row_ref.get().exists:
        raise HTTPException(status_code=404, detail="Row ID not found")

    row_ref.update({
        "fixed_category": body.fixed_category
    })

    return {"status": "ok"}
