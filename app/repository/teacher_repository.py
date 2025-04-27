from sqlalchemy.orm import Session
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate

def create_teacher(db: Session, teacher: TeacherCreate):
    db_teacher = Teacher(name=teacher.name)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

def get_teacher_by_name(db: Session, name: str):
    return db.query(Teacher).filter(Teacher.name == name).first()
