import pytest
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from app.models.teacher import Teacher
from app.core.database import Base
from app.repository.teacher_repository import TeacherRepository

# Use in-memory SQLite for fast isolated tests
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
    return TeacherRepository(db)

# === Normal behavior ===

def test_add_teacher(repo):
    teacher = repo.add("Repository Teacher")
    assert teacher.id is not None
    assert teacher.name == "Repository Teacher"

def test_get_by_id(repo):
    created = repo.add("Another Teacher")
    fetched = repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Another Teacher"

def test_get_all(repo):
    repo.add("Teacher One")
    repo.add("Teacher Two")

    all_teachers = repo.get_all()
    assert isinstance(all_teachers, list)
    assert len(all_teachers) >= 2
    assert any(t.name == "Teacher One" for t in all_teachers)

# === Weird / random / edge cases ===

def test_add_teacher_empty_string(repo):
    with pytest.raises(exc.IntegrityError):
        repo.db.add(Teacher(name=""))  # bypassing repo.add to simulate input failure
        repo.db.commit()
    repo.db.rollback()

def test_add_teacher_null(repo):
    with pytest.raises(exc.IntegrityError):
        repo.db.add(Teacher(name=None))  # nullable=False should fail
        repo.db.commit()
    repo.db.rollback()

def test_add_teacher_long_name_should_fail(repo):
    long_name = "A" * 1000  # Exceeds reasonable limit (e.g., 255)
    teacher = repo.add(long_name)

    # This should FAIL unless you explicitly constrain the field in the model
    assert len(teacher.name) <= 255, (
        "Teacher name exceeded expected max length — model should define String(255) or CheckConstraint"
    )


def test_add_teacher_unicode(repo):
    teacher = repo.add("李小龍 – 🐉 Bruce Lee")
    assert "Bruce Lee" in teacher.name

def test_add_teacher_whitespace_should_fail(repo):
    teacher = repo.add("     ")

    # This should fail unless your model or Pydantic schema strips or rejects whitespace-only names
    assert teacher.name.strip() != "", (
        "Teacher name contains only whitespace — you should enforce a non-blank constraint"
    )

def test_add_teacher_special_chars_should_fail(repo):
    name = "!@#$%^&*()_+-=~`[]{}|;:'\",.<>/?"
    teacher = repo.add(name)

    # This should fail unless you explicitly allow symbols
    assert teacher.name.isalpha(), (
        "Teacher name contains non-alphabetic characters — enforce a character whitelist or regex"
    )

def test_add_teacher_sql_injection_input(repo):
    malicious = "'; DROP TABLE teachers; --"
    teacher = repo.add(malicious)
    assert malicious in teacher.name  # SQLAlchemy escapes this safely

def test_add_teacher_duplicate(repo):
    repo.add("DuplicateName")
    with pytest.raises(exc.IntegrityError):
        repo.add("DuplicateName")  # uniqueness constraint (if defined)
    repo.db.rollback()