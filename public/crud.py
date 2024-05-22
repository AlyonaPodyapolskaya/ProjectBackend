from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_db
from typing import List
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models.models import *
from models.schemas import *
from passlib.context import CryptContext
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


security = HTTPBasic()


@router.post("/login/", tags=["Аутентификация пользователей"],
             summary="Вход пользователя с ролью репетитора или ученика")
async def login(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = await authenticate_user(credentials.username, credentials.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный username/password")
    return {"username": user.username}

async def authenticate_user(username: str, password: str, db: Session):
    async with db as session:
        result = await session.execute(select(Student).filter(Student.username == username))
        student = result.scalars().first()
        if student and pwd_context.verify(password, student.password):
            return student

        result = await session.execute(select(Tutor).filter(Tutor.username == username))
        tutor = result.scalars().first()
        if tutor and pwd_context.verify(password, tutor.password):
            return tutor

    return None

# CRUD для учеников
@router.post("/students/", response_model=StudentResponse, tags=["Ученики"],\
             summary="Создание (регистрация) пользователя с ролью ученика")
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли уже пользователь с таким именем
    existing_student = await db.execute(select(Student).filter(Student.username == student.username))
    existing_tutor = await db.execute(select(Tutor).filter(Tutor.username == student.username))

    if existing_student.scalar() or existing_tutor.scalar():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Этот username занят")

    student_data = student.dict()
    hashed_password = pwd_context.hash(student.password)
    student_data["password"] = hashed_password
    new_student = Student(**student_data)
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    return new_student

@router.get("/students/", response_model=List[StudentResponse], tags=["Ученики"],\
             summary="Получение списка всех учеников")
async def get_students(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    students = await db.execute(select(Student).offset(skip).limit(limit))
    return students.scalars().all()

@router.get("/students/{student_id}", response_model=StudentResponse, tags=["Ученики"],\
             summary="Поиск ученика по идентификатору")
async def get_student(student_id: uuid.UUID, db: Session = Depends(get_db)):
    student = await db.execute(select(Student).filter(Student.id == student_id))
    result = student.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return result

@router.put("/students/{student_id}", response_model=StudentResponse, tags=["Ученики"],\
             summary="Обновление записи об ученике по его идентификатору")
async def update_student(student_id: uuid.UUID, student: StudentUpdate, db: Session = Depends(get_db)):
    db_student = await db.execute(select(Student).filter(Student.id == student_id))
    result = db_student.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    for var, value in student.dict().items():
        setattr(result, var, value)
    await db.commit()
    await db.refresh(result)
    return result

@router.delete("/students/{student_id}", tags=["Ученики"],\
             summary="Удаление данных об ученике по его идентификатору")
async def delete_student(student_id: uuid.UUID, db: Session = Depends(get_db)):
    db_student = await db.execute(select(Student).filter(Student.id == student_id))
    result = db_student.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    await db.delete(result)
    await db.commit()
    return {"message": "Запись удалена"}

# CRUD для репетиторов
@router.post("/tutors/", response_model=TutorResponse, tags=["Репетиторы"],\
             summary="Создание (регистрация) пользователя с ролью репетитора")
async def create_tutor(tutor: TutorCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли уже пользователь с таким именем
    existing_student = await db.execute(select(Student).filter(Student.username == tutor.username))
    existing_tutor = await db.execute(select(Tutor).filter(Tutor.username == tutor.username))

    if existing_student.scalar() or existing_tutor.scalar():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Этот username занят")
    tutor_data = tutor.dict()
    hashed_password = pwd_context.hash(tutor.password)
    tutor_data["password"] = hashed_password
    new_tutor = Tutor(**tutor_data)
    db.add(new_tutor)
    await db.commit()
    await db.refresh(new_tutor)
    return new_tutor

@router.get("/tutors/", response_model=List[TutorResponse], tags=["Репетиторы"],\
             summary="Получения списка всех репетиторов")
async def get_tutors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    tutors = await db.execute(select(Tutor).offset(skip).limit(limit))
    return tutors.scalars().all()

@router.get("/tutors/{tutor_id}", response_model=TutorResponse, tags=["Репетиторы"],\
             summary="Поиск репетитора по его идентификатору")
async def get_tutor(tutor_id: uuid.UUID, db: Session = Depends(get_db)):
    tutor = await db.execute(select(Tutor).filter(Tutor.id == tutor_id))
    result = tutor.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return result

@router.put("/tutors/{tutor_id}", response_model=TutorResponse, tags=["Репетиторы"],\
             summary="Обновление записи о репетиторе по его идентификатору")
async def update_tutor(tutor_id: uuid.UUID, tutor: TutorUpdate, db: Session = Depends(get_db)):
    db_tutor = await db.execute(select(Tutor).filter(Tutor.id == tutor_id))
    result = db_tutor.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    for var, value in tutor.dict().items():
        setattr(result, var, value)
    await db.commit()
    await db.refresh(result)
    return result

@router.delete("/tutors/{tutor_id}", tags=["Репетиторы"],\
             summary="Удаление репетитора по его идентификатору")
async def delete_tutor(tutor_id: uuid.UUID, db: Session = Depends(get_db)):
    db_tutor = await db.execute(select(Tutor).filter(Tutor.id == tutor_id))
    result = db_tutor.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    await db.delete(result)
    await db.commit()
    return {"message": "Запись удалена"}

# CRUD для мест
@router.post("/places/", response_model=PlaceResponse, tags=["Места"],\
             summary="Добавление места занятий")
async def create_place(place: PlaceCreate, db: Session = Depends(get_db)):
    new_place = Place(**place.dict())
    db.add(new_place)
    await db.commit()
    await db.refresh(new_place)
    return new_place

@router.get("/places/", response_model=List[PlaceResponse], tags=["Места"],\
             summary="Список всех мест")
async def get_places(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    places = await db.execute(select(Place).offset(skip).limit(limit))
    return places.scalars().all()

@router.get("/places/{place_id}", response_model=PlaceResponse, tags=["Места"],\
             summary="Поиск места по его идентификатору")
async def get_place(place_id: uuid.UUID, db: Session = Depends(get_db)):
    place = await db.execute(select(Place).filter(Place.id == place_id))
    result = place.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return result

@router.put("/places/{place_id}", response_model=PlaceResponse, tags=["Места"],\
             summary="Обновление записи о месте")
async def update_place(place_id: uuid.UUID, place: PlaceUpdate, db: Session = Depends(get_db)):
    db_place = await db.execute(select(Place).filter(Place.id == place_id))
    result = db_place.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    for var, value in place.dict().items():
        setattr(result, var, value)
    await db.commit()
    await db.refresh(result)
    return result

@router.delete("/places/{place_id}", tags=["Места"],\
             summary="Удаление записи о месте")
async def delete_place(place_id: uuid.UUID, db: Session = Depends(get_db)):
    db_place = await db.execute(select(Place).filter(Place.id == place_id))
    result = db_place.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    await db.delete(result)
    await db.commit()
    return {"message": "Запись удалена"}

# CRUD для расписания
@router.post("/schedules/", response_model=ScheduleResponse, tags=["Расписание занятий"],\
             summary="Добавление занятие в расписание")
async def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    new_schedule = Schedule(**schedule.dict())
    db.add(new_schedule)
    await db.commit()
    await db.refresh(new_schedule)
    return new_schedule

@router.get("/schedules/", response_model=List[ScheduleResponse], tags=["Расписание занятий"],\
             summary="Получение списка всех записей о занятиях")
async def get_schedules(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    schedules = await db.execute(select(Schedule).offset(skip).limit(limit))
    return schedules.scalars().all()

@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse, tags=["Расписание занятий"],\
             summary="Поиск занятия в расписании")
async def get_schedule(schedule_id: uuid.UUID, db: Session = Depends(get_db)):
    schedule = await db.execute(select(Schedule).filter(Schedule.id == schedule_id))
    result = schedule.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return result

@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse, tags=["Расписание занятий"],\
             summary="Редактирование записи о занятии")
async def update_schedule(schedule_id: uuid.UUID, schedule: ScheduleUpdate, db: Session = Depends(get_db)):
    db_schedule = await db.execute(select(Schedule).filter(Schedule.id == schedule_id))
    result = db_schedule.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    for var, value in schedule.dict().items():
        setattr(result, var, value)
    await db.commit()
    await db.refresh(result)
    return result

@router.delete("/schedules/{schedule_id}", tags=["Расписание занятий"],\
             summary="Удаление записи о занятии")
async def delete_schedule(schedule_id: uuid.UUID, db: Session = Depends(get_db)):
    db_schedule = await db.execute(select(Schedule).filter(Schedule.id == schedule_id))
    result = db_schedule.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    await db.delete(result)
    await db.commit()
    return {"message": "Запись удалена"}

# CRUD для уведомлений
@router.post("/notifications/", response_model=NotificationResponse, tags=["Уведомления о занятиях"],\
             summary="Добавление уведомления о занятии")
async def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    new_notification = Notification(**notification.dict())
    db.add(new_notification)
    await db.commit()
    await db.refresh(new_notification)
    return new_notification

@router.get("/notifications/", response_model=List[NotificationResponse], tags=["Уведомления о занятиях"],\
             summary="Получения списка уведомлений")
async def get_notifications(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    notifications = await db.execute(select(Notification).offset(skip).limit(limit))
    return notifications.scalars().all()

@router.get("/notifications/{notification_id}", response_model=NotificationResponse, tags=["Уведомления о занятиях"],\
             summary="Поиск уведомления по идентификатору")
async def get_notification(notification_id: uuid.UUID, db: Session = Depends(get_db)):
    notification = await db.execute(select(Notification).filter(Notification.id == notification_id))
    result = notification.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return result

@router.put("/notifications/{notification_id}", response_model=NotificationResponse, tags=["Уведомления о занятиях"],\
             summary="Обновление уведомления")
async def update_notification(notification_id: uuid.UUID, notification: NotificationUpdate, db: Session = Depends(get_db)):
    db_notification = await db.execute(select(Notification).filter(Notification.id == notification_id))
    result = db_notification.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    for var, value in notification.dict().items():
        setattr(result, var, value)
    await db.commit()
    await db.refresh(result)
    return result

@router.delete("/notifications/{notification_id}", tags=["Уведомления о занятиях"],\
             summary="Удаление уведомления")
async def delete_notification(notification_id: uuid.UUID, db: Session = Depends(get_db)):
    db_notification = await db.execute(select(Notification).filter(Notification.id == notification_id))
    result = db_notification.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    await db.delete(result)
    await db.commit()
    return {"message": "Запись удалена"}

# CRUD для журнала
@router.post("/journal_entries/", response_model=JournalEntryResponse, tags=["Отслеживание прогресса обучения - журнал"],\
             summary="Добавление сведений о проведенном занятии")
async def create_journal_entry(journal_entry: JournalEntryCreate, db: Session = Depends(get_db)):
    new_journal_entry = JournalEntry(**journal_entry.dict())
    db.add(new_journal_entry)
    await db.commit()
    await db.refresh(new_journal_entry)
    return new_journal_entry

@router.get("/journal_entries/", response_model=List[JournalEntryResponse], tags=["Отслеживание прогресса обучения - журнал"],\
             summary="Получение всего журнала записей о занятиях")
async def get_journal_entries(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    journal_entries = await db.execute(select(JournalEntry).offset(skip).limit(limit))
    return journal_entries.scalars().all()

@router.get("/journal_entries/{journal_entry_id}", response_model=JournalEntryResponse, tags=["Отслеживание прогресса обучения - журнал"],\
             summary="Поиск записи в журнале")
async def get_journal_entry(journal_entry_id: uuid.UUID, db: Session = Depends(get_db)):
    journal_entry = await db.execute(select(JournalEntry).filter(JournalEntry.id == journal_entry_id))
    result = journal_entry.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return result

@router.put("/journal_entries/{journal_entry_id}", response_model=JournalEntryResponse, tags=["Отслеживание прогресса обучения - журнал"],\
             summary="Обновление записи в журнале")
async def update_journal_entry(journal_entry_id: uuid.UUID, journal_entry: JournalEntryUpdate, db: Session = Depends(get_db)):
    db_journal_entry = await db.execute(select(JournalEntry).filter(JournalEntry.id == journal_entry_id))
    result = db_journal_entry.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    for var, value in journal_entry.dict().items():
        setattr(result, var, value)
    await db.commit()
    await db.refresh(result)
    return result

@router.delete("/journal_entries/{journal_entry_id}", tags=["Отслеживание прогресса обучения - журнал"],\
             summary="Удаление записи в журнале")
async def delete_journal_entry(journal_entry_id: uuid.UUID, db: Session = Depends(get_db)):
    db_journal_entry = await db.execute(select(JournalEntry).filter(JournalEntry.id == journal_entry_id))
    result = db_journal_entry.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    await db.delete(result)
    await db.commit()

    return {"message": "Запись удалена"}
