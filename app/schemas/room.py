from pydantic import BaseModel

class RoomBase(BaseModel):
    name: str
    is_course_room: bool

class RoomCreate(RoomBase):
    pass

class RoomRead(RoomBase):
    id: int

    class Config:
        orm_mode = True
