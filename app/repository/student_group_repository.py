from sqlalchemy.orm import Session
from app.models.student_group import StudentGroup

class StudentGroupRepository:
    def __init__(self, db: Session):
        assert db is not None, "Database session must not be None"  #  Precondition
        self.db = db

    def add(self, student_year_id: int, letter: str) -> StudentGroup:
        # Preconditions
        assert isinstance(student_year_id, int) and student_year_id > 0, "student_year_id must be a positive integer"
        assert isinstance(letter, str) and letter.strip(), "letter must be a non-empty string"
        assert len(letter) == 2 and letter[0].isalpha() and letter[1].isdigit(), "letter must be in the format 'A1', 'B2', etc."
        student_group = StudentGroup(student_year_id=student_year_id, letter=letter)
        self.db.add(student_group)
        self.db.commit()
        self.db.refresh(student_group)
        # Postconditions
        assert student_group.id is not None, "Student group was not assigned an ID"
        assert student_group.student_year_id == student_year_id, "Student year ID not persisted correctly"
        assert student_group.letter == letter, "Letter not persisted correctly"
        return student_group

    def get_by_id(self, group_id: int) -> StudentGroup | None:
        assert isinstance(group_id, int) and group_id > 0, "group_id must be a positive integer"
        result = self.db.query(StudentGroup).filter(StudentGroup.id == group_id).first()
        assert (result is None or result.id == group_id), "Mismatched ID in result"
        return result
    
    def get_by_name(self, name: str) -> StudentGroup | None:
        assert isinstance(name, str) and name.strip(), "name must be a non-empty string"
        assert len(name) == 2 and name[0].isalpha() and name[1].isdigit(), "name must be in the format 'A1', 'B2', etc."
        result = self.db.query(StudentGroup).filter(StudentGroup.letter == name).first()
        assert (result is None or result.letter == name), "Mismatched letter in result"
        return result

    def get_all(self) -> list[StudentGroup]:
        results = self.db.query(StudentGroup).all()
        assert isinstance(results, list), "Results should be a list"
        return results
