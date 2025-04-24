from fastapi import APIRouter, UploadFile, File
import uuid, os, shutil

router = APIRouter()
UPLOAD_DIR = "./local_data/raw"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
def upload_dataset(file: UploadFile = File(...)):
    dataset_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"dataset_id": dataset_id, "file_path": file_path}
