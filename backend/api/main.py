import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import upload, dataset
from hooks.evaluate_trigger import router as evaluate_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(upload.router)
app.include_router(dataset.router)
app.include_router(evaluate_router)

if __name__ == "__main__":
    import uvicorn

    for route in app.routes:
        print(f"Route: {route.path} [{', '.join(route.methods)}]")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
else:
    from mangum import Mangum
    handler = Mangum(app)