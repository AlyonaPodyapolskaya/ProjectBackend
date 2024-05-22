from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class Student(Base):
    __tablename__ = "student"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lastname = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    student_class = Column(String, nullable=False)
    school = Column(String, nullable=False)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    journal_entries = relationship("JournalEntry", back_populates="student")
    notifications = relationship("Notification", back_populates="student")
    schedules = relationship("Schedule", back_populates="student")

class Tutor(Base):
    __tablename__ = "tutor"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lastname = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    schedules = relationship("Schedule", back_populates="tutor")

class Place(Base):
    __tablename__ = "place"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    address = Column(String, nullable=False)
    schedules = relationship("Schedule", back_populates="place")

class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.id"))
    tutor_id = Column(UUID(as_uuid=True), ForeignKey("tutor.id"))
    place_id = Column(UUID(as_uuid=True), ForeignKey("place.id"))
    student = relationship("Student", back_populates="schedules")
    tutor = relationship("Tutor", back_populates="schedules")
    place = relationship("Place", back_populates="schedules")
    notifications = relationship("Notification", back_populates="schedule")

class Notification(Base):
    __tablename__ = "notification"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message = Column(String, nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.id"))
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("schedule.id"))
    student = relationship("Student", back_populates="notifications")
    schedule = relationship("Schedule", back_populates="notifications")

class JournalEntry(Base):
    __tablename__ = "journal_entry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(String, nullable=False)
    content = Column(String, nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.id"))
    student = relationship("Student", back_populates="journal_entries")
