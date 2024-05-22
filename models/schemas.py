from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class StudentCreate(BaseModel):
    lastname: str
    name: str
    student_class: str
    school: str
    email: EmailStr
    username: str
    password: str

class StudentUpdate(BaseModel):
    lastname: Optional[str] = None
    name: Optional[str] = None
    student_class: Optional[str] = None
    school: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class StudentResponse(BaseModel):
    id: UUID
    lastname: str
    name: str
    student_class: str
    school: str
    email: EmailStr
    username: str

    class Config:
        orm_mode = True

class TutorCreate(BaseModel):
    lastname: str
    name: str
    email: EmailStr
    username: str
    password: str

class TutorUpdate(BaseModel):
    lastname: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class TutorResponse(BaseModel):
    id: UUID
    lastname: str
    name: str
    email: EmailStr
    username: str

    class Config:
        orm_mode = True

class PlaceCreate(BaseModel):
    name: str
    address: str

class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None

class PlaceResponse(BaseModel):
    id: UUID
    name: str
    address: str

    class Config:
        orm_mode = True

class ScheduleCreate(BaseModel):
    date: str
    time: str
    student_id: UUID
    tutor_id: UUID
    place_id: UUID

class ScheduleUpdate(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    student_id: Optional[UUID] = None
    tutor_id: Optional[UUID] = None
    place_id: Optional[UUID] = None

class ScheduleResponse(BaseModel):
    id: UUID
    date: str
    time: str
    student_id: UUID
    tutor_id: UUID
    place_id: UUID

    class Config:
        orm_mode = True

class NotificationCreate(BaseModel):
    message: str
    student_id: UUID
    schedule_id: UUID

class NotificationUpdate(BaseModel):
    message: Optional[str] = None
    student_id: Optional[UUID] = None
    schedule_id: Optional[UUID] = None

class NotificationResponse(BaseModel):
    id: UUID
    message: str
    student_id: UUID
    schedule_id: UUID

    class Config:
        orm_mode = True

class JournalEntryCreate(BaseModel):
    date: str
    content: str
    student_id: UUID

class JournalEntryUpdate(BaseModel):
    date: Optional[str] = None
    content: Optional[str] = None
    student_id: Optional[UUID] = None

class JournalEntryResponse(BaseModel):
    id: UUID
    date: str
    content: str
    student_id: UUID

    class Config:
        orm_mode = True
