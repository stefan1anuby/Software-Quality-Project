from sqlalchemy.orm import Session
from app.models.student_year import StudentYear

class StudentYearRepository:
    def __init__(self, db: Session):
        assert db is not None, "Database session must not be None"  #  Precondition
        self.db = db

    def add(self, year: int) -> StudentYear:
        assert 1 <= year < 4, "Year must be between 1 and 3 inclusive"
        student_year = StudentYear(year=year)
        self.db.add(student_year)
        self.db.commit()
        self.db.refresh(student_year)
        assert student_year.id is not None, "Student year was not assigned an ID"
        assert student_year.year == year, "Year not persisted correctly"
        return student_year

    def get_by_id(self, year_id: int) -> StudentYear | None:
        assert isinstance(year_id, int) and year_id > 0, "year_id must be a positive integer"  
        result = self.db.query(StudentYear).filter(StudentYear.id == year_id).first()
        assert (result is None or result.id == year_id), "Mismatched ID in result"  
        return result

    def get_all(self) -> list[StudentYear]:
        results = self.db.query(StudentYear).all()
        assert isinstance(results, list), "Results should be a list"
        return results
