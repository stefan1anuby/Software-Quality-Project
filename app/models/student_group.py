from sqlalchemy import CheckConstraint, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class StudentGroup(Base):
    __tablename__ = "student_groups"

    id = Column(Integer, primary_key=True, index=True)
    student_year_id = Column(Integer, ForeignKey("student_years.id"), nullable=False)
    letter = Column(String, nullable=False)

    student_year = relationship("StudentYear")

    __table_args__ = (
        CheckConstraint("letter IS NOT NULL", name="student_group_letter_not_null"),
        CheckConstraint("letter != ''", name="student_group_letter_not_empty"),
        CheckConstraint("length(letter) = 2", name="student_group_letter_length"),
        CheckConstraint("letter[0] BETWEEN 'A' AND 'Z'", name="student_group_letter_first_char"),
        CheckConstraint("letter[1] BETWEEN '0' AND '9'", name="student_group_letter_second_char"),
        CheckConstraint("student_year_id IS NOT NULL", name="student_group_student_year_not_null"),
        CheckConstraint("student_year_id > 0", name="student_group_student_year_positive")
    )
