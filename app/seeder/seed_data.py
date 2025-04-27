from app.core.database import SessionLocal
from app.models.teacher import Teacher
from app.models.room import Room

def seed_data():
    db = SessionLocal()
    if not db.query(Teacher).first():
        teachers = ["Popescu Ion", "Ionescu Maria", "Georgescu Ana"]
        for name in teachers:
            db.add(Teacher(name=name))
    if not db.query(Room).first():
        rooms = [("A1", "large"), ("Lab 101", "small")]
        for name, type in rooms:
            db.add(Room(name=name, type=type))
    db.commit()
    db.close()
