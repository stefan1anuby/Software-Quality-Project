from sqlalchemy.orm import Session
from app.models.subject import Subject, subject_teacher_association
from app.models.teacher import Teacher

class SubjectRepository:
    def __init__(self, db: Session):
        assert db is not None, "Database session must not be None"  #  Precondition
        self.db = db

    def add(self, course_teacher_id: int, student_year_id: int, name: str, seminar_lab_teacher_ids: list[int] = []) -> Subject:
        # Preconditions
        assert course_teacher_id is not None and student_year_id is not None and name is not None, "course_teacher_id, student_year_id, and name must not be None"  #  Precondition
        assert isinstance(course_teacher_id, int) and course_teacher_id > 0, "course_teacher_id must be a positive integer"
        assert isinstance(student_year_id, int) and student_year_id > 0, "student_year_id must be a positive integer"
        assert isinstance(name, str) and name.strip(), "name must be a non-empty string"
        assert isinstance(seminar_lab_teacher_ids, list) and all(isinstance(id, int) and id > 0 for id in seminar_lab_teacher_ids), "seminar_lab_teacher_ids must be a list of positive integers"
        subject = Subject(
            course_teacher_id=course_teacher_id,
            student_year_id=student_year_id,
            name=name,
        )
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)

        # Add seminar/lab teachers if provided
        if seminar_lab_teacher_ids:
            seminar_lab_teachers = self.db.query(Teacher).filter(Teacher.id.in_(seminar_lab_teacher_ids)).all()
            subject.seminar_lab_teachers = seminar_lab_teachers
            self.db.commit()

        # Postconditions
        assert subject.id is not None, "Subject was not assigned an ID"
        assert subject.course_teacher_id == course_teacher_id, "Course teacher ID not persisted correctly"
        assert subject.student_year_id == student_year_id, "Student year ID not persisted correctly"
        assert subject.name == name, "Subject name not persisted correctly"
        #assert all(teacher.id in seminar_lab_teacher_ids for teacher in subject.seminar_lab_teachers), "Seminar/lab teachers not persisted correctly"
        return subject

    def get_by_id(self, subject_id: int) -> Subject | None:
        assert isinstance(subject_id, int) and subject_id > 0, "subject_id must be a positive integer"
        result = self.db.query(Subject).filter(Subject.id == subject_id).first()
        assert (result is None or result.id == subject_id), "Mismatched ID in result"  #  Invariant
        return result

    def get_all(self) -> list[Subject]:
        results =  self.db.query(Subject).all()
        assert isinstance(results, list), "Results should be a list"
        return results
