import pytest
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from app.models.room import Room
from app.core.database import Base

# Setup an in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

# === VALID CASES ===

def test_create_room_course_type_true(db):
    room = Room(name="Room A101", is_course_room=True)
    db.add(room)
    db.commit()
    db.refresh(room)

    assert room.id is not None
    assert room.name == "Room A101"
    assert room.is_course_room is True

def test_create_room_lab_type_false(db):
    room = Room(name="Lab B201", is_course_room=False)
    db.add(room)
    db.commit()
    db.refresh(room)

    assert room.name == "Lab B201"
    assert room.is_course_room is False

# === EDGE / ERROR CASES ===

def test_create_room_duplicate_name_raises(db):
    db.add(Room(name="DUPLICATE", is_course_room=True))
    db.commit()

    with pytest.raises(exc.IntegrityError):
        db.add(Room(name="DUPLICATE", is_course_room=False))
        db.commit()
    db.rollback()

def test_create_room_null_name_fails(db):
    with pytest.raises(exc.IntegrityError):
        db.add(Room(name=None, is_course_room=True))
        db.commit()
    db.rollback()

def test_create_room_null_type_fails(db):
    with pytest.raises(exc.IntegrityError):
        db.add(Room(name="MissingTypeRoom", is_course_room=None))
        db.commit()
    db.rollback()

def test_create_room_empty_name_fails(db):
    #this should fail because there are not any constraints
    with pytest.raises(exc.IntegrityError):
        db.add(Room(name="", is_course_room=True))
        db.commit()
    db.rollback()
