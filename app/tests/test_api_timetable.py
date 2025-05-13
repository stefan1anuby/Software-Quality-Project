import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_teacher_already_existing():
    response = client.post("/api/v1/timetable/teachers/", json={"name": "Test Teacher"})
    assert response.status_code == 409 # it returns 500, that's why it fails...
    assert "id" in response.json()

def test_get_teachers():
    response = client.get("/api/v1/timetable/teachers/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_rooms():
    response = client.get("/api/v1/timetable/rooms/")
    assert response.status_code == 200

def test_create_schedule_missing_fields():
    response = client.post("/api/v1/timetable/schedule/", json={})
    assert response.status_code == 422

def test_list_schedule_by_group_not_found():
    response = client.get("/api/v1/timetable/schedule/?group_name=invalid")
    assert response.status_code == 404  # Depends on DB contents

def test_delete_schedule_not_found():
    response = client.delete("/api/v1/timetable/schedule/999999")
    assert response.status_code == 404
