import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
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
