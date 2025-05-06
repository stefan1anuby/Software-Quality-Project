from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.room import RoomRead
from app.schemas.student_group import StudentGroupRead
from app.schemas.student_year import StudentYearRead
from app.schemas.subject import SubjectRead
from app.services.timetable_service import TimetableService

from app.schemas.teacher import TeacherCreate, TeacherRead
from app.schemas.schedule_entry import ScheduleEntryCreate, ScheduleEntryRead

router = APIRouter()

@router.post("/teachers/", response_model=TeacherRead)
def create_teacher_endpoint(teacher: TeacherCreate, db: Session = Depends(get_db)):
    service = TimetableService(db)
    return service.create_teacher(teacher)

@router.get("/teachers/", response_model=List[TeacherRead])
def list_teachers_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    return service.list_teachers()

@router.get("/years/", response_model=List[StudentYearRead])
def list_years_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    return service.list_years()


@router.get("/groups/", response_model=List[StudentGroupRead])
def list_groups_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    return service.list_groups()


@router.get("/subjects/", response_model=List[SubjectRead])
def list_subjects_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    return service.list_subjects()

@router.get("/rooms/", response_model=List[RoomRead])
def list_rooms_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    return service.list_rooms()


@router.post("/schedule/", response_model=ScheduleEntryRead)
def create_schedule_entry_endpoint(entry: ScheduleEntryCreate, db: Session = Depends(get_db)):
    service = TimetableService(db)
    return service.create_schedule_entry(entry)

@router.get("/schedule/", response_model=List[ScheduleEntryRead])
def list_schedule_entries_endpoint(
    group_name: str = None, db: Session = Depends(get_db)
):
    """
    List schedule entries. Optionally filter by group name.
    """
    service = TimetableService(db)
    if group_name:
        return service.list_schedule_entries_by_group(group_name)
    return service.list_schedule_entries()
