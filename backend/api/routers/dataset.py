from fastapi import APIRouter, HTTPException
from api.models import DatasetMetrics, PatchRowRequest
import boto3, os, time

router = APIRouter()
dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("TABLE_NAME")
table = dynamodb.Table(TABLE_NAME)

@router.get("/dataset/{dataset_id}/metrics", response_model=DatasetMetrics)
def get_metrics(dataset_id: str):
    key = {"PK": f"DATASET#{dataset_id}", "SK": "METRICS"}
    item = table.get_item(Key=key).get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DatasetMetrics(**item)

@router.patch("/rows/{row_id}")
def patch_row(row_id: str, body: PatchRowRequest):
    pk, sk = row_id.split("#")
    table.update_item(
        Key={"PK": pk, "SK": sk},
        UpdateExpression="SET fixed_category = :fc, reviewed_at = :now",
        ExpressionAttributeValues={":fc": body.fixed_category, ":now": int(time.time())},
        ConditionExpression="attribute_exists(SK)"
    )
    return {"status": "ok"}