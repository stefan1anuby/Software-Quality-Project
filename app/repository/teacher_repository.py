from sqlalchemy.orm import Session
from app.models.teacher import Teacher

class TeacherRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, name: str) -> Teacher:
        teacher = Teacher(name=name)
        self.db.add(teacher)
        self.db.commit()
        self.db.refresh(teacher)
        return teacher

    def get_by_id(self, teacher_id: int) -> Teacher | None:
        return self.db.query(Teacher).filter(Teacher.id == teacher_id).first()

    def get_all(self) -> list[Teacher]:
        return self.db.query(Teacher).all()
