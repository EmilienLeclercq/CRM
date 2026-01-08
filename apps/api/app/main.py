import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import SessionLocal
from .routers import auth, deals, pipelines
from .seed import seed_initial_data

app = FastAPI(title="Lemonfive CRM API")

origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
def startup_seed():
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(pipelines.router)
app.include_router(deals.router)
