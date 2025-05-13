import pytest
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.room import Room
from app.repository.room_repository import RoomRepository

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
    return RoomRepository(db)

# === BASIC FUNCTIONALITY ===

def test_add_valid_course_room(repo):
    room = repo.add(name="TestRoomA", is_course_room=True)
    assert room.id is not None
    assert room.name == "TestRoomA"
    assert room.is_course_room is True

def test_add_valid_lab_room(repo):
    room = repo.add(name="LabX", is_course_room=False)
    assert room.is_course_room is False

def test_get_all_rooms(repo):
    repo.add(name="BulkRoom1", is_course_room=True)
    repo.add(name="BulkRoom2", is_course_room=False)
    all_rooms = repo.get_all()
    assert isinstance(all_rooms, list)
    assert len(all_rooms) >= 2

def test_get_room_by_id(repo):
    created = repo.add(name="RoomById", is_course_room=True)
    fetched = repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id

def test_get_room_by_invalid_id(repo):
    assert repo.get_by_id(999999) is None

# === EDGE CASES & VALIDATION ===

def test_add_duplicate_room_name_fails(repo):
    repo.add(name="DuplicateRoom", is_course_room=True)
    with pytest.raises(exc.IntegrityError):
        repo.add(name="DuplicateRoom", is_course_room=False)
    repo.db.rollback()

def test_add_null_name_fails(repo):
    with pytest.raises(exc.IntegrityError):
        repo.db.add(Room(name=None, is_course_room=True))
        repo.db.commit()
    repo.db.rollback()

def test_add_null_type_fails(repo):
    with pytest.raises(exc.IntegrityError):
        repo.db.add(Room(name="MissingType", is_course_room=None))
        repo.db.commit()
    repo.db.rollback()

def test_add_empty_name_fails_if_constrained(repo):
    #this should fail because there aren't any constraint
    with pytest.raises(exc.IntegrityError):
        repo.add(name="", is_course_room=True)
    repo.db.rollback()

def test_add_unicode_room_name(repo):
    room = repo.add(name="教室 101 🧪", is_course_room=True)
    assert "教室" in room.name
    assert room.name.endswith("🧪")

def test_add_very_long_room_name(repo):
    long_name = "R" * 500
    room = repo.add(name=long_name, is_course_room=False)
    
    # Fails if length exceeds what your DB *should* enforce (255 for example)
    assert len(room.name) <= 255, "Room name is too long and should have been rejected"

