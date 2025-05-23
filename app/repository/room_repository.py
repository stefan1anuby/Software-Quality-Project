from sqlalchemy.orm import Session
from app.models.room import Room

class RoomRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, name: str, is_course_room: bool) -> Room:
        room = Room(name=name, is_course_room=is_course_room)
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def get_all(self) -> list[Room]:
        return self.db.query(Room).all()

    def get_by_id(self, room_id: int) -> Room | None:
        return self.db.query(Room).filter(Room.id == room_id).first()
