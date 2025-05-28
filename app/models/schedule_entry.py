from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class ClassTypeEnum(str, enum.Enum):
    Course = "Course"
    Seminar = "Seminar"
    Laboratory = "Laboratory"

class ScheduleEntry(Base):
    __tablename__ = "schedule_entries"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String, nullable=False)

    start_hour = Column(Integer, nullable=False)
    end_hour = Column(Integer, nullable=False)

    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    student_group_id = Column(Integer, ForeignKey("student_groups.id"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    class_type = Column(Enum(ClassTypeEnum), nullable=False)

    # Relationships
    subject = relationship("Subject")
    room = relationship("Room")
    student_group = relationship("StudentGroup")
    teacher = relationship("Teacher")

    __table_args__ = (
        CheckConstraint("start_hour >= 8 AND start_hour < 20", name="start_hour_valid"),
        CheckConstraint("end_hour > start_hour AND end_hour <= 20", name="end_hour_valid"),
        CheckConstraint("end_hour - start_hour = 2", name="class_duration_2h"),
        CheckConstraint(
            "day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')",
            name="valid_weekday"
        ),
    )
