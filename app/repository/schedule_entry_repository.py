from sqlalchemy.orm import Session
from app.models.schedule_entry import ScheduleEntry

class ScheduleEntryRepository:
    def __init__(self, db: Session):
        assert db is not None, "Database session must not be None"  #  Precondition
        self.db = db

    def add(
        self,
        day_of_week: str,
        start_hour: int,
        end_hour: int,
        subject_id: int,
        room_id: int,
        teacher_id: int,
        class_type: str,
        student_group_id: int = None
    ) -> ScheduleEntry:
        #  Preconditions
        assert isinstance(day_of_week, str) and day_of_week.strip(), "day_of_week must be a non-empty string"
        assert 8 <= start_hour < 20, "start_hour must be between 8 and 19"
        assert 9 <= end_hour <= 20, "end_hour must be between 9 and 20"
        assert end_hour > start_hour, "end_hour must be after start_hour"
        assert class_type in ["Course", "Seminar", "Laboratory"], "Invalid class type"
        assert all(isinstance(i, int) for i in [subject_id, room_id, teacher_id]), "Foreign key IDs must be integers"

        schedule_entry = ScheduleEntry(
            day_of_week=day_of_week,
            start_hour=start_hour,
            end_hour=end_hour,
            subject_id=subject_id,
            room_id=room_id,
            teacher_id=teacher_id,
            class_type=class_type,
            student_group_id=student_group_id
        )

        self.db.add(schedule_entry)
        self.db.commit()
        self.db.refresh(schedule_entry)

        #  Postconditions
        assert schedule_entry.id is not None, "Schedule entry was not assigned an ID"
        assert schedule_entry.start_hour == start_hour, "start_hour not persisted correctly"
        assert schedule_entry.end_hour == end_hour, "end_hour not persisted correctly"

        return schedule_entry

    def get_by_id(self, schedule_id: int) -> ScheduleEntry | None:
        assert isinstance(schedule_id, int) and schedule_id > 0, "schedule_id must be a positive integer"  #  Precondition
        result = self.db.query(ScheduleEntry).filter(ScheduleEntry.id == schedule_id).first()
        assert (result is None or result.id == schedule_id), "Mismatched ID in result"  #  Invariant
        return result

    def get_by_group_id(self, group_id: int) -> list[ScheduleEntry]:
        assert isinstance(group_id, int), "group_id must be an integer"  #  Precondition
        results = self.db.query(ScheduleEntry).filter(ScheduleEntry.student_group_id == group_id).all()
        assert all(e.student_group_id == group_id for e in results), "Group mismatch in results"  #  Postcondition
        return results

    def get_all(self) -> list[ScheduleEntry]:
        results = self.db.query(ScheduleEntry).all()
        assert isinstance(results, list), "get_all must return a list"  #  Postcondition
        return results

    def delete(self, schedule_id: int) -> bool:
        assert isinstance(schedule_id, int) and schedule_id > 0, "schedule_id must be a positive integer"  #  Precondition
        schedule_entry = self.get_by_id(schedule_id)
        if schedule_entry:
            self.db.delete(schedule_entry)
            self.db.commit()
            assert self.get_by_id(schedule_id) is None, "Schedule entry was not deleted"  #  Postcondition
            return True
        return False
