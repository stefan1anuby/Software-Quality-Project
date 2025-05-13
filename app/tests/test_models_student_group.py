import pytest
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.student_year import StudentYear
from app.models.student_group import StudentGroup

# In-memory SQLite DB
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed at least one StudentYear
    session.add(StudentYear(year=1))
    session.commit()
    yield session
    session.close()

# === VALID CASE ===

def test_create_valid_group(db):
    year = db.query(StudentYear).first()
    group = StudentGroup(student_year_id=year.id, letter="A")
    db.add(group)
    db.commit()
    db.refresh(group)

    assert group.id is not None
    assert group.letter == "A"
    assert group.student_year_id == year.id

# === FAILURES EXPECTED ===

def test_create_group_null_year_fails(db):
    with pytest.raises(exc.IntegrityError):
        db.add(StudentGroup(student_year_id=None, letter="B"))
        db.commit()
    db.rollback()

def test_create_group_null_letter_fails(db):
    year = db.query(StudentYear).first()
    with pytest.raises(exc.IntegrityError):
        db.add(StudentGroup(student_year_id=year.id, letter=None))
        db.commit()
    db.rollback()

def test_create_group_empty_letter_should_fail(db):
    year = db.query(StudentYear).first()
    group = StudentGroup(student_year_id=year.id, letter="")
    db.add(group)
    db.commit()
    db.refresh(group)
    assert group.letter != "", "Group letter should not be empty — add CheckConstraint"

def test_create_group_long_letter_should_fail(db):
    year = db.query(StudentYear).first()
    group = StudentGroup(student_year_id=year.id, letter="ABCDEFGHIJK")
    db.add(group)
    db.commit()
    db.refresh(group)
    assert len(group.letter) <= 2, "Group letter is too long — define a String length or constraint"

def test_create_group_non_letter_should_fail(db):
    year = db.query(StudentYear).first()
    group = StudentGroup(student_year_id=year.id, letter="123")
    db.add(group)
    db.commit()
    db.refresh(group)
    assert group.letter.isalpha(), "Group letter should only contain letters — add a constraint"

def test_create_group_without_existing_year_fails(db):
    with pytest.raises(exc.IntegrityError):
        db.add(StudentGroup(student_year_id=9999, letter="Z"))
        db.commit()
    db.rollback()
