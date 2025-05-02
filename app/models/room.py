from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_course_room = Column(Boolean, nullable=False)
