from sqlalchemy import CheckConstraint, Column, Integer
from app.core.database import Base

class StudentYear(Base):
    __tablename__ = "student_years"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)  

    __table_args__ = (
        CheckConstraint("year IS NOT NULL", name="year_not_null"),
        CheckConstraint("year >= 1 AND year <= 3", name="valid_student_year")
    )
