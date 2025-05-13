import pytest
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from app.models.student_year import StudentYear
from app.core.database import Base

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

# === SHOULD PASS (VALID CASES) ===

def test_create_valid_student_year_1(db):
    year = StudentYear(year=1)
    db.add(year)
    db.commit()
    db.refresh(year)
    assert year.id is not None
    assert year.year == 1

def test_create_valid_student_year_5(db):
    year = StudentYear(year=5)
    db.add(year)
    db.commit()
    db.refresh(year)
    assert year.year == 5

# === SHOULD FAIL — NO CONSTRAINTS PRESENT YET ===

def test_create_year_zero_should_fail(db):
    year = StudentYear(year=0)
    db.add(year)
    db.commit()
    db.refresh(year)
    assert False, "Expected failure: year=0 should not be allowed without constraint"

def test_create_negative_year_should_fail(db):
    year = StudentYear(year=-3)
    db.add(year)
    db.commit()
    db.refresh(year)
    assert False, "Expected failure: negative year should not be valid"

def test_create_year_above_5_should_fail(db):
    year = StudentYear(year=10)
    db.add(year)
    db.commit()
    db.refresh(year)
    assert False, "Expected failure: year > 5 should not be allowed"

def test_create_year_null_should_fail(db):
    with pytest.raises(exc.IntegrityError):
        db.add(StudentYear(year=None))
        db.commit()
    db.rollback()

def test_create_year_as_string_should_fail(db):
    with pytest.raises(exc.IntegrityError):
        db.add(StudentYear(year="Two"))
        db.commit()
    db.rollback()
