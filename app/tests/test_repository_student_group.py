import pytest
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.student_year import StudentYear
from app.repository.student_group_repository import StudentGroupRepository
from app.models.student_group import StudentGroup

# In-memory SQLite DB
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed one student year
    session.add(StudentYear(year=1))
    session.commit()
    yield session
    session.close()

@pytest.fixture()
def repo(db):
    return StudentGroupRepository(db)

# === VALID CASE ===

def test_add_valid_student_group(repo, db):
    year = db.query(StudentYear).first()
    group = repo.add(student_year_id=year.id, letter="A")
    assert group.id is not None
    assert group.letter == "A"

def test_get_by_id(repo):
    group = repo.add(student_year_id=1, letter="B")
    fetched = repo.get_by_id(group.id)
    assert fetched is not None
    assert fetched.letter == "B"

def test_get_by_name(repo):
    group = repo.add(student_year_id=1, letter="C")
    fetched = repo.get_by_name("C")
    assert fetched is not None
    assert fetched.id == group.id

def test_get_all_groups(repo):
    repo.add(student_year_id=1, letter="D")
    groups = repo.get_all()
    assert isinstance(groups, list)
    assert any(g.letter == "D" for g in groups)

# === CONSTRAINT-DRIVEN FAILURES ===

def test_add_group_null_letter_fails(repo, db):
    with pytest.raises(exc.IntegrityError):
        db.add(StudentGroup(student_year_id=1, letter=None))
        db.commit()
    db.rollback()

def test_add_group_empty_letter_should_fail(repo):
    group = repo.add(student_year_id=1, letter="")
    assert group.letter != "", "Group letter should not be empty — enforce with CheckConstraint"

def test_add_group_long_letter_should_fail(repo):
    group = repo.add(student_year_id=1, letter="ABCDEFG")
    assert len(group.letter) <= 2, "Letter too long — add String(length) limit"

def test_add_group_non_letter_should_fail(repo):
    group = repo.add(student_year_id=1, letter="123")
    assert group.letter.isalpha(), "Letter must contain only letters — add CheckConstraint"

def test_add_group_without_existing_year_fails(db):
    with pytest.raises(exc.IntegrityError):
        db.add(StudentGroup(student_year_id=9999, letter="Z"))
        db.commit()
    db.rollback()
