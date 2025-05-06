from sqlalchemy import Column, Integer, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

subject_teacher_association = Table(
    "subject_teacher_association",
    Base.metadata,
    Column("subject_id", Integer, ForeignKey("subjects.id")),
    Column("teacher_id", Integer, ForeignKey("teachers.id"))
)

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    course_teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    student_year_id = Column(Integer, ForeignKey("student_years.id"), nullable=False)
    name = Column(String, unique=True, nullable=False)
    course_teacher = relationship("Teacher", foreign_keys=[course_teacher_id])
    seminar_lab_teachers = relationship("Teacher", secondary=subject_teacher_association)
    student_year = relationship("StudentYear")
