from fastapi import FastAPI
from app.api.v1 import timetable
from contextlib import asynccontextmanager
from app.core.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
	create_db_and_tables()

app = FastAPI()

app.include_router(timetable.router, prefix="/api/v1/timetable")

