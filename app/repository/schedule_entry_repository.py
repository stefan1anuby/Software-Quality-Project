from sqlalchemy.orm import Session
from app.models.schedule_entry import ScheduleEntry

class ScheduleEntryRepository:
    def __init__(self, db: Session):
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
        return schedule_entry

    def get_by_id(self, schedule_id: int) -> ScheduleEntry | None:
        return self.db.query(ScheduleEntry).filter(ScheduleEntry.id == schedule_id).first()
    
    def get_by_group_id(self, group_id: int) -> list[ScheduleEntry]:
        return self.db.query(ScheduleEntry).filter(ScheduleEntry.student_group_id == group_id).all()

    def get_all(self) -> list[ScheduleEntry]:
        return self.db.query(ScheduleEntry).all()
