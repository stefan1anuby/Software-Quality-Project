import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.services.timetable_service import TimetableService
from app.schemas.schedule_entry import ScheduleEntryCreate

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def service(mock_db):
    return TimetableService(mock_db)

def test_missing_fields_raises_error(service):
    with pytest.raises(ValidationError) as exc_info:
        service.create_schedule_entry(ScheduleEntryCreate(
            day_of_week=None,
            start_hour=None,
            end_hour=None,
            subject_id=None,
            room_id=None,
            teacher_id=None,
            class_type=None,
            student_group_id=None
        ))
    #assert exc_info.value.status_code == 400
    assert exc_info

def test_wrong_class_duration(service):
    entry = ScheduleEntryCreate(
        day_of_week="Monday",
        start_hour=10,
        end_hour=12 + 1,  # 3 hours instead of 2
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Course",
        student_group_id=1
    )
    with pytest.raises(HTTPException) as exc_info:
        service.create_schedule_entry(entry)
    assert exc_info.value.status_code == 400
    assert "Classes must be 2 hours long" in exc_info.value.detail

def test_invalid_day(service):
    entry = ScheduleEntryCreate(
        day_of_week="Sunday",
        start_hour=8,
        end_hour=10,
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Course",
        student_group_id=1
    )
    with pytest.raises(HTTPException) as exc_info:
        service.create_schedule_entry(entry)
    assert exc_info.value.status_code == 400
    assert "Monday to Friday" in exc_info.value.detail


def test_start_hour_after_end_hour(service):
    entry = ScheduleEntryCreate(
        day_of_week="Monday",
        start_hour=12,
        end_hour=10,
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Course",
        student_group_id=1
    )
    with pytest.raises(HTTPException) as exc_info:
        service.create_schedule_entry(entry)
    assert exc_info.value.status_code == 400
    assert "End hour must be after start hour" in exc_info.value.detail

def test_start_hour_between_8_and_20(service):
    entry = ScheduleEntryCreate(
        day_of_week="Tuesday",
        start_hour=7,
        end_hour=9,
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Course",
        student_group_id=1
    )
    with pytest.raises(HTTPException) as exc_info:
        service.create_schedule_entry(entry)
    assert exc_info.value.status_code == 400
    assert 'Classes must be scheduled between 8 and 20.' in exc_info.value.detail

def test_end_hour_between_8_and_20(service):
    entry = ScheduleEntryCreate(
        day_of_week="Wednesday",
        start_hour=16,
        end_hour=21,
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Course",
        student_group_id=1
    )
    with pytest.raises(HTTPException) as exc_info:
        service.create_schedule_entry(entry)
    assert exc_info.value.status_code == 400
    assert 'Classes must be scheduled between 8 and 20.' in exc_info.value.detail

def test_teacher_already_occupied(service):

    # Inject mocked repositories
    service.schedule_repo = MagicMock()

    existing_entry = MagicMock()
    existing_entry.day_of_week = "Tuesday"
    existing_entry.start_hour = 11
    existing_entry.end_hour = 13
    existing_entry.teacher_id = 5

    service.schedule_repo.get_all = MagicMock(return_value=[existing_entry])  

    new_entry = ScheduleEntryCreate(
        day_of_week="Tuesday",
        start_hour=11,
        end_hour=13,
        subject_id=3,
        room_id=2,
        teacher_id=5,  # same teacher
        class_type="Seminar",
        student_group_id=4
    )

    with pytest.raises(HTTPException) as exc_info:
        service.create_schedule_entry(new_entry)

    assert exc_info.value.status_code == 400
    assert "Teacher is already scheduled at that time." in exc_info.value.detail


def test_room_already_occupied(service):
    
    service.schedule_repo = MagicMock()
   
    existing_entry = MagicMock()
    existing_entry.day_of_week = "Monday"
    existing_entry.start_hour = 8
    existing_entry.end_hour = 10
    existing_entry.room_id = 1

    service.schedule_repo.get_all.return_value = [existing_entry]

    new_entry = ScheduleEntryCreate(
        day_of_week="Monday",
        start_hour=8,
        end_hour=10,
        subject_id=2,
        room_id=1,  # same room
        teacher_id=2,
        class_type="Course",
        student_group_id=2
    )

    with pytest.raises(HTTPException) as exc_info:
        service.create_schedule_entry(new_entry)

    assert exc_info.value.status_code == 400
    assert "Room is already occupied at that time" in exc_info.value.detail


def test_room_not_found(service):
    # Mock the room_repo to simulate a non-existing room
    service.room_repo = MagicMock()
    service.room_repo.get_by_id.return_value = None

    entry = ScheduleEntryCreate(
        day_of_week="Monday",
        start_hour=8,
        end_hour=10,
        subject_id=1,
        room_id=1,  
        teacher_id=1,
        class_type="Course",
        student_group_id=1
    )
    with pytest.raises(HTTPException) as exc_info:
        service.create_schedule_entry(entry)
    assert exc_info.value.status_code == 404
    assert "Room not found" in exc_info.value.detail

def test_course_room_type(service):
    # Mock the room_repo to simulate a non-course room
    service.room_repo = MagicMock()
    service.room_repo.get_by_id.return_value = MagicMock(is_course_room=False)

    entry = ScheduleEntryCreate(
        day_of_week="Monday",
        start_hour=8,
        end_hour=10,
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Course",
        student_group_id=1
    )
    with pytest.raises(HTTPException) as exc_info:
        service.create_schedule_entry(entry)
    assert exc_info.value.status_code == 400
    assert 'Courses must be held in course rooms.' in exc_info.value.detail

def test_seminar_room_type(service):
    # Mock the room_repo to simulate a seminar room
    service.room_repo = MagicMock()
    service.room_repo.get_by_id.return_value = MagicMock(is_course_room=True)

    entry = ScheduleEntryCreate(
        day_of_week="Monday",
        start_hour=8,
        end_hour=10,
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Seminar",
        student_group_id=1
    )
    with pytest.raises(HTTPException) as exc_info:
        service.create_schedule_entry(entry)
    assert exc_info.value.status_code == 400
    assert 'Labs and seminars must be in lab rooms.' in exc_info.value.detail

def test_laboratory_room_type(service):
    # Mock the room_repo to simulate a seminar room
    service.room_repo = MagicMock()
    service.room_repo.get_by_id.return_value = MagicMock(is_course_room=True)

    entry = ScheduleEntryCreate(
        day_of_week="Monday",
        start_hour=8,
        end_hour=10,
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Laboratory",
        student_group_id=1
    )
    with pytest.raises(HTTPException) as exc_info:
        service.create_schedule_entry(entry)
    assert exc_info.value.status_code == 400
    assert 'Labs and seminars must be in lab rooms.' in exc_info.value.detail


def test_group_not_found(service):
    # Mock the student_group_repo to simulate a non-existing group
    service.student_group_repo = MagicMock()
    service.student_group_repo.get_by_name.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.list_schedule_entries_by_group('XYZ')
    assert exc_info.value.status_code == 404
    assert "Group not found" in exc_info.value.detail

def test_schedule_entry_not_found(service):
    # Mock the schedule_repo to simulate a non-existing entry
    service.schedule_repo = MagicMock()
    service.schedule_repo.delete.return_value = None

    entry = ScheduleEntryCreate(
        day_of_week="Monday",
        start_hour=8,
        end_hour=10,
        subject_id=1,
        room_id=1,
        teacher_id=1,
        class_type="Course",
        student_group_id=1
    )
    with pytest.raises(HTTPException) as exc_info:
        service.delete_schedule_entry(entry)
    assert exc_info.value.status_code == 404
    assert 'Schedule entry not found.' in exc_info.value.detail



