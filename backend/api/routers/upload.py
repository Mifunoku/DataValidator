from fastapi import APIRouter
import boto3, uuid, os

router = APIRouter()
s3 = boto3.client("s3")
RAW_BUCKET = os.environ.get("RAW_BUCKET")

@router.post("/upload")
def upload_dataset():
    dataset_id = str(uuid.uuid4())
    key = f"raw/{dataset_id}.csv"
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": RAW_BUCKET, "Key": key, "ContentType": "text/csv"},
        ExpiresIn=600,
    )
    return {"dataset_id": dataset_id, "upload_url": url}
