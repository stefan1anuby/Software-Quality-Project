from fastapi import APIRouter, Depends, HTTPException
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
    assert teacher is not None, "TeacherCreate payload is required"  #  Precondition
    service = TimetableService(db)
    result = service.create_teacher(teacher)
    assert result.name == teacher.name, "Teacher creation postcondition failed"  #  Postcondition
    return result

@router.get("/teachers/", response_model=List[TeacherRead])
def list_teachers_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    result = service.list_teachers()
    assert isinstance(result, list), "Teachers must be returned as a list"  #  Postcondition
    return result

@router.get("/years/", response_model=List[StudentYearRead])
def list_years_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    result = service.list_years()
    assert all(y.year >= 1 for y in result), "Invalid year value found"  #  Postcondition
    return result

@router.get("/groups/", response_model=List[StudentGroupRead])
def list_groups_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    result = service.list_groups()
    assert all(g.letter for g in result), "Group with empty letter found"  #  Postcondition
    return result

@router.get("/subjects/", response_model=List[SubjectRead])
def list_subjects_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    result = service.list_subjects()
    assert all(s.name for s in result), "Subject with no name found"  #  Postcondition
    return result

@router.get("/rooms/", response_model=List[RoomRead])
def list_rooms_endpoint(db: Session = Depends(get_db)):
    service = TimetableService(db)
    result = service.list_rooms()
    assert all(isinstance(r.is_course_room, bool) for r in result), "Room type inconsistency"  #  Postcondition
    return result

@router.post("/schedule/", response_model=ScheduleEntryRead)
def create_schedule_entry_endpoint(entry: ScheduleEntryCreate, db: Session = Depends(get_db)):
    assert entry is not None, "ScheduleEntryCreate payload is required"  #  Precondition
    service = TimetableService(db)
    result = service.create_schedule_entry(entry)
    assert result.start_hour == entry.start_hour, "Mismatch in start_hour after creation"  #  Postcondition
    return result

@router.get("/schedule/", response_model=List[ScheduleEntryRead])
def list_schedule_entries_endpoint(group_name: str = None, db: Session = Depends(get_db)):
    service = TimetableService(db)
    if group_name:
        assert isinstance(group_name, str) and group_name.strip(), "Group name must be non-empty string"  #  Precondition
        result = service.list_schedule_entries_by_group(group_name)
        assert all(e.student_group_id for e in result), "Entries without group_id found"  #  Postcondition
        return result
    result = service.list_schedule_entries()
    assert isinstance(result, list), "Schedule list must be of type list"  #  Postcondition
    return result

@router.delete("/schedule/{schedule_id}", status_code=204)
def delete_schedule_entry_endpoint(schedule_id: int, db: Session = Depends(get_db)):
    assert isinstance(schedule_id, int) and schedule_id > 0, "schedule_id must be a positive integer"  #  Precondition
    service = TimetableService(db)
    success = service.delete_schedule_entry(schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule entry not found")
    assert success is True, "Expected schedule entry deletion to succeed"  #  Postcondition