from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class StudentGroup(Base):
    __tablename__ = "student_groups"

    id = Column(Integer, primary_key=True, index=True)
    student_year_id = Column(Integer, ForeignKey("student_years.id"), nullable=False)
    letter = Column(String, nullable=False)

    student_year = relationship("StudentYear")
