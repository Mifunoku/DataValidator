from fastapi import FastAPI
from mangum import Mangum
from api.routers import upload, dataset

app = FastAPI()
app.include_router(upload.router)
app.include_router(dataset.router)

handler = Mangum(app)  # AWS Lambda entry point
