import pytest
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.student_year import StudentYear

# In-memory test DB
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed teacher and year
    teacher = Teacher(name="John Smith")
    year = StudentYear(year=1)
    session.add_all([teacher, year])
    session.commit()
    yield session
    session.close()

# === VALID CASE ===

def test_create_valid_subject(db):
    teacher = db.query(Teacher).first()
    year = db.query(StudentYear).first()

    subject = Subject(
        name="Mathematics",
        course_teacher_id=teacher.id,
        student_year_id=year.id
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)

    assert subject.id is not None
    assert subject.name == "Mathematics"

# === FAILURES EXPECTED IF NO CONSTRAINTS ===

def test_create_subject_null_name_fails(db):
    teacher = db.query(Teacher).first()
    year = db.query(StudentYear).first()
    with pytest.raises(exc.IntegrityError):
        db.add(Subject(name=None, course_teacher_id=teacher.id, student_year_id=year.id))
        db.commit()
    db.rollback()

def test_create_subject_empty_name_should_fail(db):
    teacher = db.query(Teacher).first()
    year = db.query(StudentYear).first()
    subject = Subject(name="", course_teacher_id=teacher.id, student_year_id=year.id)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    assert subject.name != "", "Empty subject name accepted — add CheckConstraint or validation"

def test_create_subject_long_name_should_fail(db):
    teacher = db.query(Teacher).first()
    year = db.query(StudentYear).first()
    long_name = "A" * 1000
    subject = Subject(name=long_name, course_teacher_id=teacher.id, student_year_id=year.id)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    assert len(subject.name) <= 255, "Subject name exceeds 255 chars — add length limit"

def test_create_subject_whitespace_name_should_fail(db):
    teacher = db.query(Teacher).first()
    year = db.query(StudentYear).first()
    subject = Subject(name="     ", course_teacher_id=teacher.id, student_year_id=year.id)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    assert subject.name.strip() != "", "Whitespace-only name accepted — enforce TRIM constraint"

def test_create_subject_without_teacher_fails(db):
    year = db.query(StudentYear).first()
    with pytest.raises(exc.IntegrityError):
        db.add(Subject(name="NoTeacher", course_teacher_id=None, student_year_id=year.id))
        db.commit()
    db.rollback()

def test_create_subject_without_year_fails(db):
    teacher = db.query(Teacher).first()
    with pytest.raises(exc.IntegrityError):
        db.add(Subject(name="NoYear", course_teacher_id=teacher.id, student_year_id=None))
        db.commit()
    db.rollback()

def test_create_subject_with_non_existing_fk_ids_fails(db):
    with pytest.raises(exc.IntegrityError):
        db.add(Subject(name="GhostLinks", course_teacher_id=9999, student_year_id=9999))
        db.commit()
    db.rollback()
