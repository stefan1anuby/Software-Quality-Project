from sqlalchemy import CheckConstraint, Column, Integer, String, Boolean
from app.core.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_course_room = Column(Boolean, nullable=False)

    __table_args__ = (
        CheckConstraint("name IS NOT NULL", name="room_name_not_null"),
        CheckConstraint("name != ''", name="room_name_not_empty"),
        CheckConstraint("is_course_room IN (0, 1)", name="room_is_course_room_valid")
    )
