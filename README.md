# Software-Quality-Project
# 📘 University Timetable API

A FastAPI-based backend for managing university timetable scheduling with validations, teacher and room constraints, and automatic conflict prevention.

---

## 🧱 Project Architecture

```
app/
├── api/
│   └── v1/
│       └── timetable.py         # Endpoints for all core features
├── core/
│   └── database.py              # Database connection and initialization
├── models/                      # SQLAlchemy ORM models
├── repository/                  # Database access layer
├── schemas/                     # Pydantic schemas
├── services/
│   └── timetable_service.py     # Business logic and validations
├── seeder/
│   └── seed_data.py             # Seeds initial data
├── main.py                      # App entry point
frontend/
```

---

## 📊 Data Models

### `Room`

```python
id: int (PK)
name: str
is_course_room: bool  # True for lectures, False for seminars/labs
```

### `Teacher`

```python
id: int (PK)
name: str
```

### `StudentYear`

```python
id: int (PK)
year: int  # 1 to 5
```

### `StudentGroup`

```python
id: int (PK)
name: str
year_id: FK -> StudentYear
```

### `Subject`

```python
id: int (PK)
name: str
year_id: FK -> StudentYear
course_teacher_id: FK -> Teacher
seminar_lab_teacher_id: FK -> Teacher
```

### `ScheduleEntry`

```python
id: int (PK)
day_of_week: Enum('Monday'...'Friday')
start_hour: int (0-23)
end_hour: int (0-23)
teacher_id: FK -> Teacher
subject_id: FK -> Subject
room_id: FK -> Room
student_group_id: FK -> StudentGroup (nullable)
class_type: Enum('Course', 'Seminar', 'Lab')
```

---

## 📦 Repositories

Each model has a repository providing basic CRUD operations.

### Example: `RoomRepository`

```python
def get_all() -> list[Room]
def get_by_id(id: int) -> Room | None
def add(name: str, is_course_room: bool) -> Room
```

Similar repositories:

* `TeacherRepository`
* `StudentGroupRepository`
* `StudentYearRepository`
* `SubjectRepository`
* `ScheduleEntryRepository`

---

## 🧠 Timetable Service (`services/timetable_service.py`)

Handles business rules and validations.

### `create_schedule_entry(entry: ScheduleEntryCreate)`

* Must be exactly 2 hours
* Time must be within 08:00–20:00
* No overlapping for teacher or room
* Room must match class type
* Allowed days: Monday to Friday

Raises `HTTPException` for invalid requests.

### Other methods

* `list_schedule_entries()`
* `delete_schedule_entry(id)`
* Lookup: `list_teachers()`, `list_rooms()`, `list_groups()`, `list_years()`, `list_subjects()`

---

## 📂 Schemas (`schemas/`)

### `ScheduleEntryCreate`

```python
class ScheduleEntryCreate(BaseModel):
    day_of_week: Literal['Monday'...'Friday']
    start_hour: int
    end_hour: int
    teacher_id: int
    subject_id: int
    room_id: int
    student_group_id: Optional[int]
    class_type: Literal['Course', 'Seminar', 'Lab']
```

---

## 🌐 API Routes (`api/v1/timetable.py`)

| Method | Endpoint                          | Description                 |
| ------ | --------------------------------- | --------------------------- |
| GET    | `/teachers`                       | List all teachers           |
| GET    | `/rooms`                          | List all rooms              |
| GET    | `/groups`                         | List student groups         |
| GET    | `/years`                          | List academic years         |
| GET    | `/subjects`                       | List subjects               |
| GET    | `/schedule-entries`               | List scheduled classes      |
| POST   | `/schedule-entries`               | Create a new schedule entry |
| DELETE | `/schedule-entries/{schedule_id}` | Delete a schedule entry     |

---

## 🌱 Seeder (`seeder/seed_data.py`)

Seeds the database with:

* Teachers
* Years
* Groups
* Rooms
* Subjects
* Schedule Entries

---

## 🚩 Validation Rules Summary

| Rule          | Description                                     |
| ------------- | ----------------------------------------------- |
| ⏰ Time        | Classes must be **2 hours**, 08:00–20:00        |
| 📅 Days       | Only **Monday–Friday** allowed                  |
| 👩‍🏫 Teacher | Cannot overlap with another class               |
| 🏫 Room       | Cannot overlap at same time                     |
| 🏋️ Match     | Course in course room, Seminar/Lab in lab rooms |

---

## 🌟 How to Run

```bash
uvicorn app.main:app --reload
python3 -m http.server 3000
```

App starts on `http://localhost:8000` and `http://localhost:3000/frontend/index.html`

---

## 🔪 Postman Tests Available

A Postman collection is included to test the API endpoints:

| Test Name       | Method | Endpoint                          |
| --------------- | ------ | --------------------------------- |
| Get Schedules   | GET    | `/api/v1/timetable/schedule/`     |
| Get Teachers    | GET    | `/api/v1/timetable/teachers/`     |
| Get Groups      | GET    | `/api/v1/timetable/groups/`       |
| Get Subjects    | GET    | `/api/v1/timetable/subjects/`     |
| Get Rooms       | GET    | `/api/v1/timetable/rooms/`        |
| Get Years       | GET    | `/api/v1/timetable/years/`        |
| Create Schedule | POST   | `/api/v1/timetable/schedule/`     |
| Delete Schedule | DELETE | `/api/v1/timetable/schedule/{id}` |

Make sure the app is running locally on port `8000` for the collection to work correctly.

---

🖥️ Frontend Overview
![image](https://github.com/user-attachments/assets/faf19aec-4854-4ab1-ba32-27ebfc7cd611)
![image](https://github.com/user-attachments/assets/4875d2f0-3b02-4a1d-a48e-1af9f6b024ec)

---
🖥️ Swagger Documentation
![image](https://github.com/user-attachments/assets/e6b470f8-5cc5-4e73-abd7-24f5dad7e1f1)

![image](https://github.com/user-attachments/assets/01eba3c1-b86d-4877-b3e6-fe22ae3a4460)
---
## 🎓 Future Improvements

* UI for Admins & Students
* Schedule filtering per group/teacher
* Export to PDF/CSV
* Weekly view endpoint

---

## 📦 Dependencies

* FastAPI
* SQLAlchemy
* Pydantic
* Uvicorn

---

