from sqlalchemy.orm import Session
from app.models.student_group import StudentGroup

class StudentGroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, student_year_id: int, letter: str) -> StudentGroup:
        student_group = StudentGroup(student_year_id=student_year_id, letter=letter)
        self.db.add(student_group)
        self.db.commit()
        self.db.refresh(student_group)
        return student_group

    def get_by_id(self, group_id: int) -> StudentGroup | None:
        return self.db.query(StudentGroup).filter(StudentGroup.id == group_id).first()
    
    def get_by_name(self, name: str) -> StudentGroup | None:
        return self.db.query(StudentGroup).filter(StudentGroup.letter == name).first()

    def get_all(self) -> list[StudentGroup]:
        return self.db.query(StudentGroup).all()
