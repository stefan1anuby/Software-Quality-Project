from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.schedule_entry import ScheduleEntryCreate, ScheduleEntryRead
from app.services.timetable_service import create_schedule_entry

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/schedule/", response_model=ScheduleEntryRead)
def create_schedule(entry: ScheduleEntryCreate, db: Session = Depends(get_db)):
    return create_schedule_entry(db, entry)
