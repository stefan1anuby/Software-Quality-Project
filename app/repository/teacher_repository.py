from sqlalchemy.orm import Session
from app.models.teacher import Teacher

class TeacherRepository:
    def __init__(self, db: Session):
        assert db is not None, "Database session must not be None"  #  Precondition
        self.db = db

    def add(self, name: str) -> Teacher:       
        assert name is not None and isinstance(name, str) and name.strip(), "Name must be a non-empty string"
        teacher = Teacher(name=name)
        self.db.add(teacher)
        self.db.commit()
        self.db.refresh(teacher)
        assert teacher.id is not None, "Teacher was not assigned an ID"
        assert teacher.name == name, "Teacher name not persisted correctly"
        return teacher

    def get_by_id(self, teacher_id: int) -> Teacher | None:
        assert isinstance(teacher_id, int) and teacher_id > 0, "teacher_id must be a positive integer"
        result = self.db.query(Teacher).filter(Teacher.id == teacher_id).first()
        assert (result is None or result.id == teacher_id), "Mismatched ID in result"
        return result

    def get_all(self) -> list[Teacher]:
        results = self.db.query(Teacher).all()
        assert isinstance(results, list), "Results should be a list"
        return results
