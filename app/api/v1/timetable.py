from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.timetable_service import TimetableService

from app.schemas.teacher import TeacherCreate, TeacherRead
from app.schemas.schedule_entry import ScheduleEntryCreate, ScheduleEntryRead

router = APIRouter()

@router.post("/teachers/", response_model=TeacherRead)
def create_teacher_endpoint(teacher: TeacherCreate, db: Session = Depends(get_db)):
    service = TimetableService(db)
    return service.create_teacher(teacher)

@router.post("/schedule/", response_model=ScheduleEntryRead)
def create_schedule_entry_endpoint(entry: ScheduleEntryCreate, db: Session = Depends(get_db)):
    service = TimetableService(db)
    return service.create_schedule_entry(entry)

@router.get("/teachers/", response_model=List[TeacherRead])
def list_teachers_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    return service.list_teachers()

@router.get("/schedule/", response_model=List[ScheduleEntryRead])
def list_schedule_entries_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    return service.list_schedule_entries()
