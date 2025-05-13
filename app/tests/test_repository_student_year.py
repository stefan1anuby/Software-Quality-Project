import pytest
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.repository.student_year_repository import StudentYearRepository
from app.models.student_year import StudentYear

# In-memory SQLite test DB
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture()
def repo(db):
    return StudentYearRepository(db)

# === VALID CASES ===

def test_add_valid_student_year(repo):
    year = repo.add(1)
    assert year.id is not None
    assert year.year == 1

def test_get_all_student_years(repo):
    repo.add(2)
    repo.add(3)
    result = repo.get_all()
    assert isinstance(result, list)
    assert any(y.year == 2 for y in result)

def test_get_by_id_existing(repo):
    year = repo.add(4)
    fetched = repo.get_by_id(year.id)
    assert fetched is not None
    assert fetched.year == 4

def test_get_by_id_not_found(repo):
    assert repo.get_by_id(999999) is None

# === FAILURES EXPECTED (TO ENFORCE MODEL CONSTRAINTS) ===

def test_add_year_zero_should_fail(repo):
    year = repo.add(0)
    assert year.year >= 1, "Year must be >= 1 — define constraint in model"

def test_add_negative_year_should_fail(repo):
    year = repo.add(-2)
    assert year.year >= 1, "Negative year accepted — should be blocked by DB constraint"

def test_add_year_above_5_should_fail(repo):
    year = repo.add(999)
    assert year.year <= 5, "Year above 5 accepted — define upper bound constraint"

def test_add_null_year_should_fail(repo):
    with pytest.raises(exc.IntegrityError):
        repo.db.add(StudentYear(year=None))
        repo.db.commit()
    repo.db.rollback()

def test_add_string_instead_of_int_should_fail(repo):
    with pytest.raises(Exception):  # Type error or StatementError
        repo.db.add(StudentYear(year="First"))
        repo.db.commit()
    repo.db.rollback()
