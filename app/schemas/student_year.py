from pydantic import BaseModel

class StudentYearBase(BaseModel):
    year: int  # 1..5

class StudentYearCreate(StudentYearBase):
    pass

class StudentYearRead(StudentYearBase):
    id: int

    class Config:
        orm_mode = True
