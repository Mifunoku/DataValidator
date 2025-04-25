from fastapi import APIRouter, UploadFile, File
from google.cloud import storage
import uuid

router = APIRouter()

# GCS client
storage_client = storage.Client()
RAW_BUCKET = "ds-raw-files"  # <-- your raw bucket name

@router.post("/upload")
def upload_dataset(file: UploadFile = File(...)):
    dataset_id = str(uuid.uuid4())
    print("Uploading dataset with ID:", dataset_id)

    bucket = storage_client.bucket(RAW_BUCKET)
    blob = bucket.blob(f"raw/{dataset_id}.csv")

    # Upload file to GCS directly
    blob.upload_from_file(file.file, rewind=True)

    return {"dataset_id": dataset_id}
