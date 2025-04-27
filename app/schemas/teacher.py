from pydantic import BaseModel

class TeacherCreate(BaseModel):
    name: str

class TeacherRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
