import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import upload, dataset
from api.routers.evaluate_trigger import router as evaluate_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://storage.googleapis.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(upload.router)
app.include_router(dataset.router)
app.include_router(evaluate_router)


