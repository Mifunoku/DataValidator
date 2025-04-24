from fastapi import APIRouter
from functions.evaluate.app import evaluate_local

router = APIRouter()


@router.post("/evaluate/{dataset_id}")
def evaluate_dataset(dataset_id: str):
    try:
        evaluate_local(dataset_id)
        return {"status": "success", "message": f"Evaluated {dataset_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
