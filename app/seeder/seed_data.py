from app.core.database import SessionLocal
from app.repository.teacher_repository import TeacherRepository
from app.repository.room_repository import RoomRepository
from app.repository.student_year_repository import StudentYearRepository
from app.repository.student_group_repository import StudentGroupRepository
from app.repository.subject_repository import SubjectRepository
from app.repository.schedule_entry_repository import ScheduleEntryRepository

def seed_data():
    db = SessionLocal()

    try:
        teacher_repo = TeacherRepository(db)
        room_repo = RoomRepository(db)
        year_repo = StudentYearRepository(db)
        group_repo = StudentGroupRepository(db)
        subject_repo = SubjectRepository(db)
        schedule_repo = ScheduleEntryRepository(db)

        # --- Seed Teachers ---
        if not teacher_repo.get_all():
            t1 = teacher_repo.add(name="Ion Popescu")
            t2 = teacher_repo.add(name="Maria Ionescu")
            t3 = teacher_repo.add(name="Andrei Georgescu")

        # --- Seed Student Years ---
        if not year_repo.get_all():
            year1 = year_repo.add(year=1)
            year2 = year_repo.add(year=2)

        # --- Seed Student Groups ---
        if not group_repo.get_all():
            g1 = group_repo.add(student_year_id=year1.id, letter="A")
            g2 = group_repo.add(student_year_id=year1.id, letter="B")
            g3 = group_repo.add(student_year_id=year2.id, letter="A")

        # --- Seed Rooms ---
        if not room_repo.get_all():
            r1 = room_repo.add(name="Room A1", is_course_room=True)
            r2 = room_repo.add(name="Lab 101", is_course_room=False)
            r3 = room_repo.add(name="Lab 102", is_course_room=False)
            r4 = room_repo.add(name="Room A2", is_course_room=True)

        # --- Seed Subjects ---
        if not subject_repo.get_all():
            # Subject 1: for year 1, course by t1, labs by t2 and t3
            subj1 = subject_repo.add(
                course_teacher_id=t1.id,
                student_year_id=year1.id,
                seminar_lab_teacher_ids=[t2.id, t3.id]
            )
            # Subject 2: for year 2, course by t2, labs by t3
            subj2 = subject_repo.add(
                course_teacher_id=t2.id,
                student_year_id=year2.id,
                seminar_lab_teacher_ids=[t3.id]
            )

        # --- Seed Schedule Entries ---
        if not schedule_repo.get_all():
            # Course - no group attached
            schedule_repo.add(
                day_of_week="Monday",
                start_hour=8,
                end_hour=10,
                subject_id=subj1.id,
                room_id=r1.id,
                teacher_id=t1.id,  # course teacher
                class_type="Course",
                student_group_id=None
            )

            # Seminar for Group A
            schedule_repo.add(
                day_of_week="Tuesday",
                start_hour=10,
                end_hour=12,
                subject_id=subj1.id,
                room_id=r2.id,
                teacher_id=t2.id,  # seminar/lab teacher
                class_type="Seminar",
                student_group_id=g1.id
            )

            # Lab for Group B
            schedule_repo.add(
                day_of_week="Tuesday",
                start_hour=12,
                end_hour=14,
                subject_id=subj1.id,
                room_id=r3.id,
                teacher_id=t3.id,
                class_type="Laboratory",
                student_group_id=g2.id
            )

            # Course for second year
            schedule_repo.add(
                day_of_week="Wednesday",
                start_hour=8,
                end_hour=10,
                subject_id=subj2.id,
                room_id=r1.id,
                teacher_id=t2.id,
                class_type="Course",
                student_group_id=None
            )

    finally:
        db.close()
