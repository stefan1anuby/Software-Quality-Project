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

def test_add_teacher_long_name(repo):
    name = "A" * 1000  # SQLite doesn't enforce length unless specified
    teacher = repo.add(name)
    assert teacher.name == name
    assert len(teacher.name) == 1000

def test_add_teacher_unicode(repo):
    teacher = repo.add("李小龍 – 🐉 Bruce Lee")
    assert "Bruce Lee" in teacher.name

def test_add_teacher_whitespace(repo):
    teacher = repo.add("     ")
    assert teacher.name.strip() == "" or teacher.name == "     "  # depends on policy

def test_add_teacher_special_chars(repo):
    name = "!@#$%^&*()_+-=~`[]{}|;:'\",.<>/?"
    teacher = repo.add(name)
    assert teacher.name == name

def test_add_teacher_sql_injection_input(repo):
    malicious = "'; DROP TABLE teachers; --"
    teacher = repo.add(malicious)
    assert malicious in teacher.name  # SQLAlchemy escapes this safely

def test_add_teacher_duplicate(repo):
    repo.add("DuplicateName")
    with pytest.raises(exc.IntegrityError):
        repo.add("DuplicateName")  # uniqueness constraint (if defined)
    repo.db.rollback()