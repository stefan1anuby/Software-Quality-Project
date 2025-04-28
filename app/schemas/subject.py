from pydantic import BaseModel
from typing import List

class SubjectBase(BaseModel):
    course_teacher_id: int
    student_year_id: int
    seminar_lab_teacher_ids: List[int] = []

class SubjectCreate(SubjectBase):
    pass

class SubjectRead(SubjectBase):
    id: int

    class Config:
        orm_mode = True
