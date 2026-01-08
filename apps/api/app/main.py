from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, deals, pipelines, stages
from app.db.session import SessionLocal
from app.seed import seed_data

app = FastAPI(title="Lemonfive CRM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(pipelines.router)
app.include_router(stages.router)
app.include_router(deals.router)


@app.on_event("startup")
def startup_seed() -> None:
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
