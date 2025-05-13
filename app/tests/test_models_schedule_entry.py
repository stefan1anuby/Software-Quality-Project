import pytest
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.teacher import Teacher
from app.models.room import Room
from app.models.subject import Subject
from app.models.student_year import StudentYear
from app.models.student_group import StudentGroup
from app.models.schedule_entry import ScheduleEntry

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    teacher = Teacher(name="Prof. X")
    room = Room(name="Room 101", is_course_room=True)
    year = StudentYear(year=1)
    session.add_all([teacher, room, year])
    session.commit()

    subject = Subject(name="AI", course_teacher_id=teacher.id, student_year_id=year.id)
    group = StudentGroup(student_year_id=year.id, letter="A")
    session.add_all([subject, group])
    session.commit()

    yield session
    session.close()

def create_entry(**overrides):
    base = dict(
        day_of_week="Monday",
        start_hour=8,
        end_hour=10,
        subject_id=1,
        room_id=1,
        student_group_id=1,
        teacher_id=1,
        class_type="Course"
    )
    base.update(overrides)
    return ScheduleEntry(**base)

# Valid
def test_create_valid_entry(db):
    entry = create_entry()
    db.add(entry)
    db.commit()
    db.refresh(entry)
    assert entry.id is not None

# Failures for missing or broken values
def test_start_hour_out_of_bounds(db):
    entry = create_entry(start_hour=6, end_hour=8)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    assert 8 <= entry.start_hour <= 20, "Start hour out of allowed range"

def test_end_hour_out_of_bounds(db):
    entry = create_entry(start_hour=18, end_hour=21)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    assert entry.end_hour <= 20, "End hour exceeds allowed time"

def test_class_duration_invalid(db):
    entry = create_entry(start_hour=10, end_hour=11)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    assert entry.end_hour - entry.start_hour == 2, "Class must be 2 hours"

def test_invalid_class_type(db):
    entry = create_entry(class_type="Workshop")
    db.add(entry)
    db.commit()
    db.refresh(entry)
    assert entry.class_type in ["Course", "Seminar", "Laboratory"], "Invalid class type"

def test_invalid_day_of_week(db):
    entry = create_entry(day_of_week="Sunday")
    db.add(entry)
    db.commit()
    db.refresh(entry)
    assert entry.day_of_week in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "Invalid day"

def test_missing_teacher_id(db):
    with pytest.raises(exc.IntegrityError):
        db.add(create_entry(teacher_id=None))
        db.commit()
    db.rollback()

def test_missing_subject_id(db):
    with pytest.raises(exc.IntegrityError):
        db.add(create_entry(subject_id=None))
        db.commit()
    db.rollback()

def test_missing_room_id(db):
    with pytest.raises(exc.IntegrityError):
        db.add(create_entry(room_id=None))
        db.commit()
    db.rollback()

def test_missing_class_type(db):
    with pytest.raises(exc.IntegrityError):
        db.add(create_entry(class_type=None))
        db.commit()
    db.rollback()

# Conflicts
def test_schedule_entry_teacher_overlap(db):
    db.add(create_entry(start_hour=12, end_hour=14))
    db.commit()

    entry = create_entry(start_hour=13, end_hour=15)
    db.add(entry)
    db.commit()
    db.refresh(entry)

    assert not (12 < entry.end_hour and 14 > entry.start_hour), "Teacher overlaps another class"

def test_schedule_entry_room_overlap(db):
    db.add(create_entry(start_hour=14, end_hour=16))
    db.commit()

    entry = create_entry(start_hour=15, end_hour=17)
    db.add(entry)
    db.commit()
    db.refresh(entry)

    assert not (14 < entry.end_hour and 16 > entry.start_hour), "Room overlaps another class"

def test_class_type_course_must_be_in_course_room(db):
    teacher = db.query(Teacher).first()
    subject = db.query(Subject).first()
    group = db.query(StudentGroup).first()

    # Create a non-course room (lab)
    lab_room = Room(name="Lab Room", is_course_room=False)
    db.add(lab_room)
    db.commit()

    entry = ScheduleEntry(
        day_of_week="Tuesday",
        start_hour=10,
        end_hour=12,
        subject_id=subject.id,
        room_id=lab_room.id,
        student_group_id=group.id,
        teacher_id=teacher.id,
        class_type="Course"
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    assert lab_room.is_course_room is True, "Course class held in lab room — should fail"
    
def test_class_type_lab_in_wrong_room_type(db):
    teacher = db.query(Teacher).first()
    subject = db.query(Subject).first()
    group = db.query(StudentGroup).first()
    course_room = db.query(Room).filter_by(name="Room 101").first()

    entry = ScheduleEntry(
        day_of_week="Wednesday",
        start_hour=8,
        end_hour=10,
        subject_id=subject.id,
        room_id=course_room.id,
        student_group_id=group.id,
        teacher_id=teacher.id,
        class_type="Laboratory"
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    assert not course_room.is_course_room, "Laboratory held in course room — should fail"
    
def test_teacher_not_associated_with_subject(db):
    unrelated_teacher = Teacher(name="Ghost Teacher")
    db.add(unrelated_teacher)
    db.commit()

    subject = db.query(Subject).first()
    room = db.query(Room).first()
    group = db.query(StudentGroup).first()

    entry = ScheduleEntry(
        day_of_week="Friday",
        start_hour=10,
        end_hour=12,
        subject_id=subject.id,
        room_id=room.id,
        student_group_id=group.id,
        teacher_id=unrelated_teacher.id,
        class_type="Seminar"
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    is_valid = (entry.teacher_id == subject.course_teacher_id or
                any(t.id == entry.teacher_id for t in subject.seminar_lab_teachers))
    assert is_valid, "Teacher not associated with subject — must enforce rule"