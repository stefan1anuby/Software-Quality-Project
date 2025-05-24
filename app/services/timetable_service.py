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
        # PRECONDITIONS
        assert entry_data is not None, "entry_data must not be None"
        assert isinstance(entry_data.start_hour, int), "start_hour must be an integer"
        assert isinstance(entry_data.end_hour, int), "end_hour must be an integer"
        assert entry_data.class_type in ["Course", "Seminar", "Laboratory"], "Invalid class_type"

        if any(val is None for val in [
            entry_data.start_hour,
            entry_data.end_hour,
            entry_data.day_of_week,
            entry_data.room_id,
            entry_data.teacher_id,
            entry_data.subject_id,
            entry_data.class_type,
            entry_data.student_group_id
        ]):
            raise HTTPException(status_code=400, detail="All fields are required.")

        assert 8 <= entry_data.start_hour < 20, "start_hour out of range"
        assert 9 <= entry_data.end_hour <= 20, "end_hour out of range"
        assert entry_data.end_hour > entry_data.start_hour, "end_hour must be after start_hour"
        assert entry_data.end_hour - entry_data.start_hour == 2, "Classes must be 2 hours long"
        assert entry_data.day_of_week in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "Invalid day"

        # INVARIANTS
        entries_same_room = self.schedule_repo.get_all()
        for existing in entries_same_room:
            assert existing is not None
            if (existing.room_id == entry_data.room_id and
                existing.day_of_week == entry_data.day_of_week and
                not (entry_data.end_hour <= existing.start_hour or entry_data.start_hour >= existing.end_hour)):
                raise HTTPException(status_code=400, detail="Room is already occupied at that time.")

        entries_same_teacher = self.schedule_repo.get_all()
        for existing in entries_same_teacher:
            assert existing.teacher_id is not None
            if (existing.teacher_id == entry_data.teacher_id and
                existing.day_of_week == entry_data.day_of_week and
                not (entry_data.end_hour <= existing.start_hour or entry_data.start_hour >= existing.end_hour)):
                raise HTTPException(status_code=400, detail="Teacher is already scheduled at that time.")

        room = self.room_repo.get_by_id(entry_data.room_id)
        assert isinstance(room, Room), "Expected a Room instance"
        if not room:
            raise HTTPException(status_code=404, detail="Room not found.")

        if entry_data.class_type == "Course":
            assert room.is_course_room is True, "Courses must be in course rooms"
        if entry_data.class_type in ["Laboratory", "Seminar"]:
            assert room.is_course_room is False, "Labs/seminars must be in lab rooms"

        # POSTCONDITION
        schedule = self.schedule_repo.add(
            day_of_week=entry_data.day_of_week,
            start_hour=entry_data.start_hour,
            end_hour=entry_data.end_hour,
            subject_id=entry_data.subject_id,
            room_id=entry_data.room_id,
            teacher_id=entry_data.teacher_id,
            class_type=entry_data.class_type,
            student_group_id=entry_data.student_group_id,
        )

        assert schedule.id is not None, "Schedule was not persisted"
        assert schedule.day_of_week == entry_data.day_of_week, "Day mismatch after insert"
        return schedule

    
    def list_schedule_entries(self):
        entries = self.schedule_repo.get_all()
        assert isinstance(entries, list), "Schedule entries must be a list"
        return entries
    
    def create_teacher(self, teacher_data: TeacherCreate):
        assert teacher_data is not None, "Teacher data must be provided"
        assert isinstance(teacher_data.name, str), "Teacher name must be a string"
        assert teacher_data.name.strip() != "", "Teacher name cannot be empty"

        teacher = self.teacher_repo.add(name=teacher_data.name)

        assert teacher.id is not None, "Teacher must have an ID after creation"
        assert teacher.name == teacher_data.name, "Teacher name mismatch"

        return teacher

    
    def list_teachers(self):
        teachers = self.teacher_repo.get_all()
        assert isinstance(teachers, list), "Teachers must be a list"
        assert all(t.name for t in teachers), "Each teacher must have a name"
        return teachers

    def list_groups(self):
        groups = self.student_group_repo.get_all()
        assert isinstance(groups, list), "Groups must be a list"
        assert all(g.letter for g in groups), "Each group must have a letter"
        return groups

    def list_years(self):
        years = self.year_repo.get_all()
        assert isinstance(years, list), "Years must be a list"
        assert all(y.year >= 1 for y in years), "Invalid student year value"
        return years

    def list_rooms(self):
        rooms = self.room_repo.get_all()
        assert isinstance(rooms, list), "Rooms must be a list"
        assert all(isinstance(r.is_course_room, bool) for r in rooms), "Room type must be boolean"
        return rooms

    def list_subjects(self):
        subjects = self.subject_repo.get_all()
        assert isinstance(subjects, list), "Subjects must be a list"
        assert all(s.name for s in subjects), "Each subject must have a name"
        return subjects

    def list_schedule_entries_by_group(self, group_name: str):
        assert isinstance(group_name, str), "Group name must be a string"
        assert group_name.strip() != "", "Group name cannot be empty"

        group = self.student_group_repo.get_by_name(group_name)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found.")

        results = self.schedule_repo.get_by_group_id(group.id)
        assert all(e.student_group_id == group.id for e in results), "Mismatched group entries returned"
        return results

    def delete_schedule_entry(self, schedule_id: int) -> bool:
        assert isinstance(schedule_id, int), "Schedule ID must be an integer"
        assert schedule_id > 0, "Schedule ID must be positive"

        success = self.schedule_repo.delete(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule entry not found.")
        return True

    
