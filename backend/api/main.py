from fastapi import FastAPI
from api.routers import upload, dataset
from hooks.evaluate_trigger import router as evaluate_router

app = FastAPI()
app.include_router(upload.router)
app.include_router(dataset.router)
app.include_router(evaluate_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
else:
    from mangum import Mangum
    handler = Mangum(app)  # AWS Lambda entry point
