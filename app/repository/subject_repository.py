from sqlalchemy.orm import Session
from app.models.subject import Subject, subject_teacher_association
from app.models.teacher import Teacher

class SubjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, course_teacher_id: int, student_year_id: int, seminar_lab_teacher_ids: list[int] = []) -> Subject:
        subject = Subject(
            course_teacher_id=course_teacher_id,
            student_year_id=student_year_id
        )
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)

        # Add seminar/lab teachers if provided
        if seminar_lab_teacher_ids:
            seminar_lab_teachers = self.db.query(Teacher).filter(Teacher.id.in_(seminar_lab_teacher_ids)).all()
            subject.seminar_lab_teachers = seminar_lab_teachers
            self.db.commit()

        return subject

    def get_by_id(self, subject_id: int) -> Subject | None:
        return self.db.query(Subject).filter(Subject.id == subject_id).first()

    def get_all(self) -> list[Subject]:
        return self.db.query(Subject).all()
