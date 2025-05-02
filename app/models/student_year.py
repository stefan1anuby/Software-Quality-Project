from sqlalchemy import Column, Integer
from app.core.database import Base

class StudentYear(Base):
    __tablename__ = "student_years"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)  # 1..5
