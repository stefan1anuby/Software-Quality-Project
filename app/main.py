from fastapi import FastAPI
from app.api.v1 import timetable
from contextlib import asynccontextmanager
from app.core.database import create_db_and_tables
from app.seeder.seed_data import seed_data

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_data()

app.include_router(timetable.router, prefix="/api/v1/timetable")

