import pytest
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.teacher import Teacher
from app.models.student_year import StudentYear
from app.repository.subject_repository import SubjectRepository
from app.models.subject import Subject

# In-memory SQLite test DB
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed some teachers and a student year
    t1 = Teacher(name="Course Teacher")
    t2 = Teacher(name="Lab Teacher")
    y1 = StudentYear(year=1)
    session.add_all([t1, t2, y1])
    session.commit()

    yield session
    session.close()

@pytest.fixture()
def repo(db):
    return SubjectRepository(db)

# === VALID CASES ===

def test_add_subject_without_seminar_teachers(repo, db):
    course_teacher = db.query(Teacher).filter_by(name="Course Teacher").first()
    year = db.query(StudentYear).first()

    subject = repo.add(
        course_teacher_id=course_teacher.id,
        student_year_id=year.id,
        name="Math"
    )

    assert subject.id is not None
    assert subject.name == "Math"
    assert subject.course_teacher_id == course_teacher.id
    assert len(subject.seminar_lab_teachers) == 0

def test_add_subject_with_seminar_teachers(repo, db):
    course_teacher = db.query(Teacher).filter_by(name="Course Teacher").first()
    seminar_teacher = db.query(Teacher).filter_by(name="Lab Teacher").first()
    year = db.query(StudentYear).first()

    subject = repo.add(
        course_teacher_id=course_teacher.id,
        student_year_id=year.id,
        name="Physics",
        seminar_lab_teacher_ids=[seminar_teacher.id]
    )

    assert subject.name == "Physics"
    assert len(subject.seminar_lab_teachers) == 1
    assert seminar_teacher in subject.seminar_lab_teachers

def test_get_subject_by_id(repo):
    subject = repo.add(1, 1, "Chemistry")
    fetched = repo.get_by_id(subject.id)
    assert fetched is not None
    assert fetched.name == "Chemistry"

def test_get_all_subjects(repo):
    subjects = repo.get_all()
    assert isinstance(subjects, list)
    assert len(subjects) >= 1

# === FAILURE-DRIVEN TESTS ===

def test_add_subject_with_null_name_fails(db):
    with pytest.raises(exc.IntegrityError):
        db.add(Subject(name=None, course_teacher_id=1, student_year_id=1))
        db.commit()
    db.rollback()

def test_add_subject_with_empty_name_should_fail(repo):
    subject = repo.add(course_teacher_id=1, student_year_id=1, name="")
    assert subject.name != "", "Empty name should be rejected — add CheckConstraint or validation"

def test_add_subject_with_whitespace_name_should_fail(repo):
    subject = repo.add(course_teacher_id=1, student_year_id=1, name="    ")
    assert subject.name.strip() != "", "Whitespace-only name should be rejected"

def test_add_subject_with_long_name_should_fail(repo):
    long_name = "A" * 1000
    subject = repo.add(course_teacher_id=1, student_year_id=1, name=long_name)
    assert len(subject.name) <= 255, "Name too long — enforce String(255)"

def test_add_subject_with_invalid_teacher_fails(db):
    with pytest.raises(exc.IntegrityError):
        db.add(Subject(name="Ghost", course_teacher_id=9999, student_year_id=1))
        db.commit()
    db.rollback()

def test_add_subject_with_invalid_year_fails(db):
    with pytest.raises(exc.IntegrityError):
        db.add(Subject(name="Ghost", course_teacher_id=1, student_year_id=9999))
        db.commit()
    db.rollback()
