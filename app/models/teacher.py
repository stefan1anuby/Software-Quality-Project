from sqlalchemy import CheckConstraint, Column, Integer, String
from app.core.database import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    __table_args__ = (
        CheckConstraint("name IS NOT NULL", name="teacher_name_not_null"),
        CheckConstraint("name != ''", name="teacher_name_not_empty")
    )
