from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ScheduleEntry(Base):
    __tablename__ = "schedule_entries"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String, nullable=False)
    start_hour = Column(Integer, nullable=False)

    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    student_group_id = Column(Integer, ForeignKey("student_groups.id"), nullable=True)  # optional for courses
    class_type = Column(String, nullable=False)  # "Course", "Laboratory", "Seminar"

    subject = relationship("Subject")
    room = relationship("Room")
    student_group = relationship("StudentGroup")
