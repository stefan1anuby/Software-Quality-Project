from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repository.student_group_repository import StudentGroupRepository
from app.repository.student_year_repository import StudentYearRepository
from app.repository.subject_repository import SubjectRepository
from app.repository.teacher_repository import TeacherRepository
from app.repository.room_repository import RoomRepository
from app.repository.schedule_entry_repository import ScheduleEntryRepository
from app.schemas.teacher import TeacherCreate
from app.schemas.schedule_entry import ScheduleEntryCreate
from app.models.room import Room

class TimetableService:
    def __init__(self, db: Session):
        self.db = db
        self.teacher_repo = TeacherRepository(db)
        self.student_group_repo = StudentGroupRepository(db)  # Assuming you have a StudentGroupRepository
        self.year_repo = StudentYearRepository(db)  # Assuming you have a StudentYearRepository, initialize it here
        self.room_repo = RoomRepository(db)
        self.schedule_repo = ScheduleEntryRepository(db)
        self.subject_repo = SubjectRepository(db)  # Assuming you have a SubjectRepository, initialize it here

    def create_schedule_entry(self, entry_data: ScheduleEntryCreate):

        if entry_data.start_hour == None or entry_data.end_hour == None or entry_data.day_of_week == None or entry_data.room_id == None or entry_data.teacher_id == None or entry_data.subject_id == None or entry_data.class_type == None or entry_data.student_group_id == None:
            raise HTTPException(status_code=400, detail="All fields are required.")
        # 1. Check hours between 8-20
        if not (8 <= entry_data.start_hour < 20) or not (9 <= entry_data.end_hour <= 20):
            raise HTTPException(status_code=400, detail="Classes must be scheduled between 8 and 20.")
        
        if entry_data.end_hour - entry_data.start_hour != 2:
            raise HTTPException(status_code=400, detail="Classes must be 2 hours long.")

        if entry_data.start_hour >= entry_data.end_hour:
            raise HTTPException(status_code=400, detail="End hour must be after start hour.")

        # 2. Check if day is Monday-Friday
        if entry_data.day_of_week not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            raise HTTPException(status_code=400, detail="Classes must be scheduled Monday to Friday.")
        


        # 3. Check if room is available
        entries_same_room = self.schedule_repo.get_all()
        for existing in entries_same_room:
            if (
                existing.room_id == entry_data.room_id
                and existing.day_of_week == entry_data.day_of_week
                and not (entry_data.end_hour <= existing.start_hour or entry_data.start_hour >= existing.end_hour)
            ):
                raise HTTPException(status_code=400, detail="Room is already occupied at that time.")

        # 4. Check if teacher is available
        entries_same_teacher = self.schedule_repo.get_all()
        for existing in entries_same_teacher:
            if (
                existing.teacher_id == entry_data.teacher_id
                and existing.day_of_week == entry_data.day_of_week
                and not (entry_data.end_hour <= existing.start_hour or entry_data.start_hour >= existing.end_hour)
            ):
                raise HTTPException(status_code=400, detail="Teacher is already scheduled at that time.")

        # 5. Check if room type matches class type
        room = self.room_repo.get_by_id(entry_data.room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found.")

        if entry_data.class_type == "Course" and not room.is_course_room:
            raise HTTPException(status_code=400, detail="Courses must be held in course rooms.")

        if entry_data.class_type in ["Laboratory", "Seminar"] and room.is_course_room:
            raise HTTPException(status_code=400, detail="Labs and seminars must be in lab rooms.")

        # (Optional) Check if teacher actually teaches the subject — advanced rule
        # (Optional) Check if group matches subject's year — advanced rule

        # 6. If all validations pass, save entry
        return self.schedule_repo.add(
            day_of_week=entry_data.day_of_week,
            start_hour=entry_data.start_hour,
            end_hour=entry_data.end_hour,
            subject_id=entry_data.subject_id,
            room_id=entry_data.room_id,
            teacher_id=entry_data.teacher_id,
            class_type=entry_data.class_type,
            student_group_id=entry_data.student_group_id,
        )
    
    def list_schedule_entries(self):
        return self.schedule_repo.get_all()
    
    def create_teacher(self, teacher_data: TeacherCreate):
        return self.teacher_repo.add(name=teacher_data.name)
    
    def list_teachers(self):
        return self.teacher_repo.get_all()
    
    def list_groups(self):
        return self.student_group_repo.get_all()
    
    def list_years(self):
        return self.year_repo.get_all()
    
    def list_rooms(self):
        return self.room_repo.get_all()
    
    
    def list_subjects(self):
        return self.subject_repo.get_all()
    
    def list_schedule_entries_by_group(self, group_name: str):
        group = self.student_group_repo.get_by_name(group_name)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found.")
        return self.schedule_repo.get_by_group_id(group.id)

    def delete_schedule_entry(self, schedule_id: int) -> bool:
        success = self.schedule_repo.delete(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule entry not found.")
        return True

    
