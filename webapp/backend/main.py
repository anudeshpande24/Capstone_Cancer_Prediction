from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import data

app = FastAPI(title="Cancer Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(data.router)


@app.get("/health")
def health():
    return {"status": "ok"}
