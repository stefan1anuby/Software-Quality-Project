from sqlalchemy.orm import Session
from app.models.room import Room

class RoomRepository:
    def __init__(self, db: Session):
        assert db is not None, "Database session must not be None"  #  Precondition
        self.db = db

    def add(self, name: str, is_course_room: bool) -> Room:
        # Preconditions
        assert name is not None and isinstance(name, str) and name.strip(), "Name must be a non-empty string"
        assert isinstance(is_course_room, bool), "is_course_room must be a boolean value"
        room = Room(name=name, is_course_room=is_course_room)
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        # Postconditions
        assert room.id is not None, "Room was not assigned an ID"
        assert room.name == name, "Room name not persisted correctly"
        assert room.is_course_room == is_course_room, "Room type not persisted correctly"
        return room

    def get_all(self) -> list[Room]:
        results = self.db.query(Room).all()
        assert isinstance(results, list), "Results should be a list"
        return results

    def get_by_id(self, room_id: int) -> Room | None:
        assert isinstance(room_id, int) and room_id > 0, "room_id must be a positive integer"
        result = self.db.query(Room).filter(Room.id == room_id).first()
        assert (result is None or result.id == room_id), "Mismatched ID in result"
        return result
