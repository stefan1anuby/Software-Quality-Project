import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.teacher import Teacher
from app.models.room import Room
from app.models.subject import Subject
from app.models.student_year import StudentYear
from app.models.student_group import StudentGroup
from app.repository.schedule_entry_repository import ScheduleEntryRepository

# Setup in-memory SQLite test DB
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed data
    teacher = Teacher(name="Dr. Repo")
    room = Room(name="Repo Room", is_course_room=True)
    year = StudentYear(year=1)
    session.add_all([teacher, room, year])
    session.commit()

    subject = Subject(name="Repo Subject", course_teacher_id=teacher.id, student_year_id=year.id)
    group = StudentGroup(student_year_id=year.id, letter="B")
    session.add_all([subject, group])
    session.commit()

    yield session
    session.close()

@pytest.fixture()
def repo(db):
    return ScheduleEntryRepository(db)

def test_add_valid_schedule_entry(repo):
    entry = repo.add(
        day_of_week="Monday",
        start_hour=8,
        end_hour=10,
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Course",
        student_group_id=1
    )
    assert entry.id is not None
    assert entry.day_of_week == "Monday"

def test_get_schedule_entry_by_id(repo):
    new_entry = repo.add(
        day_of_week="Tuesday",
        start_hour=10,
        end_hour=12,
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Seminar",
        student_group_id=1
    )
    fetched = repo.get_by_id(new_entry.id)
    assert fetched is not None
    assert fetched.id == new_entry.id

def test_get_schedule_by_group_id(repo):
    results = repo.get_by_group_id(1)
    assert isinstance(results, list)
    assert all(entry.student_group_id == 1 for entry in results)

def test_get_all_schedule_entries(repo):
    all_entries = repo.get_all()
    assert isinstance(all_entries, list)
    assert len(all_entries) >= 2

def test_delete_existing_schedule_entry(repo):
    entry = repo.add(
        day_of_week="Wednesday",
        start_hour=12,
        end_hour=14,
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Laboratory",
        student_group_id=1
    )
    success = repo.delete(entry.id)
    assert success is True
    assert repo.get_by_id(entry.id) is None

def test_delete_nonexistent_schedule_entry(repo):
    result = repo.delete(schedule_id=9999)
    assert result is False

def test_add_with_null_day_of_week(repo):
    with pytest.raises(Exception):
        repo.add(day_of_week=None, start_hour=8, end_hour=10, subject_id=1, room_id=1,
                 teacher_id=1, class_type="Course", student_group_id=1)

def test_add_with_null_class_type(repo):
    with pytest.raises(Exception):
        repo.add(day_of_week="Monday", start_hour=8, end_hour=10, subject_id=1, room_id=1,
                 teacher_id=1, class_type=None, student_group_id=1)

# TODOOOO !!!!!!!!!!! REWRITE THE TESTS DOWN THERE (OR WRITE THEM BETTER)
def test_add_with_start_hour_after_end_hour(repo):
    entry = repo.add(day_of_week="Thursday", start_hour=14, end_hour=12, subject_id=1, room_id=1,
                     teacher_id=1, class_type="Course", student_group_id=1)
    assert entry.start_hour < entry.end_hour, "Start hour must be less than end hour"

def test_add_with_same_teacher_and_overlapping_time(repo):
    entry1 = repo.add(day_of_week="Monday", start_hour=10, end_hour=12, subject_id=1,
                      room_id=1, teacher_id=1, class_type="Seminar", student_group_id=1)
    entry2 = repo.add(day_of_week="Monday", start_hour=11, end_hour=13, subject_id=1,
                      room_id=1, teacher_id=1, class_type="Seminar", student_group_id=1)

    overlap = not (entry1.end_hour <= entry2.start_hour or entry1.start_hour >= entry2.end_hour)
    assert not overlap, "Teacher schedule should not overlap"

def test_add_with_same_room_and_overlapping_time(repo):
    entry1 = repo.add(day_of_week="Tuesday", start_hour=10, end_hour=12, subject_id=1,
                      room_id=1, teacher_id=1, class_type="Laboratory", student_group_id=1)
    entry2 = repo.add(day_of_week="Tuesday", start_hour=11, end_hour=13, subject_id=1,
                      room_id=1, teacher_id=1, class_type="Laboratory", student_group_id=1)

    overlap = not (entry1.end_hour <= entry2.start_hour or entry1.start_hour >= entry2.end_hour)
    assert not overlap, "Room schedule should not overlap"

def test_add_with_nonexistent_foreign_keys(repo):
    with pytest.raises(Exception):
        repo.add(day_of_week="Wednesday", start_hour=14, end_hour=16, subject_id=999,
                 room_id=999, teacher_id=999, class_type="Course", student_group_id=999)

def test_add_with_extremely_long_day_of_week(repo):
    long_day = "M" * 1000
    entry = repo.add(day_of_week=long_day, start_hour=8, end_hour=10, subject_id=1,
                     room_id=1, teacher_id=1, class_type="Course", student_group_id=1)
    assert len(entry.day_of_week) <= 15, "Day of week is too long — enforce length limit"

def test_add_with_invalid_class_type(repo):
    entry = repo.add(day_of_week="Thursday", start_hour=8, end_hour=10, subject_id=1,
                     room_id=1, teacher_id=1, class_type="Workshop", student_group_id=1)
    assert entry.class_type in ["Course", "Seminar", "Laboratory"], "Invalid class type"