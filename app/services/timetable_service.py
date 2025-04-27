from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.teacher import TeacherCreate, TeacherRead
from app.schemas.schedule_entry import ScheduleEntryCreate

from app.models.schedule_entry import ScheduleEntry

from app.repository.teacher_repository import create_teacher, get_teacher_by_name

router = APIRouter()
        
def create_schedule_entry(db: Session, entry: ScheduleEntryCreate):
    # 1. Verifică dacă ora e între 8-20 și ziua între Monday-Friday
    if not (8 <= entry.start_hour <= 20):
        raise HTTPException(status_code=400, detail="Classes must be scheduled between 8-20.")
    
    if entry.day_of_week not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        raise HTTPException(status_code=400, detail="Classes must be scheduled Monday-Friday.")

    # 2. Verifică dacă sala e liberă în ziua și ora respectivă
    existing_entry = schedule_repository.get_schedule_by_room_and_time(db, entry.room_id, entry.day_of_week, entry.start_hour)
    if existing_entry:
        raise HTTPException(status_code=400, detail="Room is already occupied at that time.")
    
    # 3. Verifică dacă profesorul nu are deja alt curs atunci
    prof_entry = schedule_repository.get_schedule_by_teacher_and_time(db, entry.teacher_id, entry.day_of_week, entry.start_hour)
    if prof_entry:
        raise HTTPException(status_code=400, detail="Teacher is already scheduled at that time.")

    # 4. Verifică dacă tipul sălii e corect (ex: laborator pentru laborator, curs pentru curs)
    room = room_repository.get_room_by_id(db, entry.room_id)
    if entry.class_type == "Course" and room.type != "large":
        raise HTTPException(status_code=400, detail="Courses must be held in large rooms.")
    if entry.class_type == "Laboratory" and room.type != "small":
        raise HTTPException(status_code=400, detail="Laboratories must be held in small rooms.")

    # 5. Verifică dacă profesorul predă materia (optional daca vrei sa fii strict)
    # 6. Verifică dacă grupa are acea materie anul respectiv (optional avansat)

    # Dacă toate validările sunt ok, salvăm
    return schedule_repository.create_schedule_entry(db, entry)

@router.post("/teachers/", response_model=TeacherRead)
def create_teacher_endpoint(teacher: TeacherCreate, db: Session = Depends(get_db)):
    return create_teacher(db, teacher)
