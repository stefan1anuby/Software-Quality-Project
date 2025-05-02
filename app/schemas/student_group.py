from pydantic import BaseModel

class StudentGroupBase(BaseModel):
    student_year_id: int
    letter: str

class StudentGroupCreate(StudentGroupBase):
    pass

class StudentGroupRead(StudentGroupBase):
    id: int

    class Config:
        orm_mode = True
