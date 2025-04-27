from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.seeder.seed_data import seed_data

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_db_and_tables():
    from app.models import teacher, room, student_group, subject, schedule_entry
    Base.metadata.create_all(bind=engine)
    seed_data()
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
