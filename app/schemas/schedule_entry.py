from pydantic import BaseModel
from typing import Optional

class ScheduleEntryBase(BaseModel):
    day_of_week: str  # e.g., "Monday"
    start_hour: int
    end_hour: int
    subject_id: int
    room_id: int
    teacher_id: int
    class_type: str  # "Course", "Laboratory", "Seminar"
    student_group_id: Optional[int] = None

class ScheduleEntryCreate(ScheduleEntryBase):
    pass

class ScheduleEntryRead(ScheduleEntryBase):
    id: int

    class Config:
        orm_mode = True
