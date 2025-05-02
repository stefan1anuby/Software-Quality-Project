from fastapi import FastAPI
from app.api.v1 import timetable
from contextlib import asynccontextmanager
from app.core.database import create_db_and_tables
from app.seeder.seed_data import seed_data
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # or ["http://localhost:8000", "http://127.0.0.1:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_data()

app.include_router(timetable.router, prefix="/api/v1/timetable")
# app.mount("/", StaticFiles(directory="app/frontend", html=True), name="frontend")

