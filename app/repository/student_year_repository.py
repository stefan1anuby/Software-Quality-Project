from sqlalchemy.orm import Session
from app.models.student_year import StudentYear

class StudentYearRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, year: int) -> StudentYear:
        student_year = StudentYear(year=year)
        self.db.add(student_year)
        self.db.commit()
        self.db.refresh(student_year)
        return student_year

    def get_by_id(self, year_id: int) -> StudentYear | None:
        return self.db.query(StudentYear).filter(StudentYear.id == year_id).first()

    def get_all(self) -> list[StudentYear]:
        return self.db.query(StudentYear).all()
