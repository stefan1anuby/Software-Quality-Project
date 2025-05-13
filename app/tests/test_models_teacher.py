import pytest
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from app.models.teacher import Teacher
from app.core.database import Base

# Use an in-memory SQLite DB for isolated tests
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

def test_create_teacher_model(db):
    teacher = Teacher(name="Test Model Teacher")
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    assert teacher.id is not None
    assert teacher.name == "Test Model Teacher"
    
def test_teacher_name_too_long(db):
    long_name = "A" * 100000 
    teacher = Teacher(name=long_name)
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    assert teacher.id is not None
    assert len(teacher.name) == 100000  # If no constraint, this will pass
    
def test_teacher_empty_name_fails(db):
    with pytest.raises(exc.IntegrityError):
        db.add(Teacher(name=None))
        db.commit()
    db.rollback()
