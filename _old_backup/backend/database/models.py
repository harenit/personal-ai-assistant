import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, default="Alex Rivers")
    email = Column(String(100), unique=True, nullable=False, default="alex.rivers@university.edu")
    student_id = Column(String(50), default="STU-2026-8842")
    major = Column(String(100), default="Computer Science & Artificial Intelligence")
    semester = Column(String(50), default="Fall 2026 / Senior Year")
    created_at = Column(DateTime, default=datetime.utcnow)

class Course(Base):
    __tablename__ = "courses"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(20), unique=True, nullable=False)  # e.g. CS401
    name = Column(String(100), nullable=False)              # e.g. Artificial Intelligence
    instructor = Column(String(100), nullable=False)
    instructor_email = Column(String(100), nullable=False)
    room = Column(String(50), default="Hall 304")
    schedule = Column(String(100), default="Mon/Wed 10:00 AM - 11:30 AM")
    description = Column(Text, default="")
    
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="course", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="course", cascade="all, delete-orphan")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    due_date = Column(DateTime, nullable=False)
    points = Column(Integer, default=100)
    status = Column(String(30), default="pending")  # pending, submitted, graded
    submission_text = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    grade = Column(Float, nullable=True)
    
    course = relationship("Course", back_populates="assignments")

class Exam(Base):
    __tablename__ = "exams"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    date = Column(DateTime, nullable=False)
    start_time = Column(String(20), default="10:00 AM")
    end_time = Column(String(20), default="12:00 PM")
    room = Column(String(50), default="Hall 304")
    topics = Column(Text, default="")
    weight_percent = Column(Integer, default=30)
    
    course = relationship("Course", back_populates="exams")

class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_urgent = Column(Boolean, default=False)
    
    course = relationship("Course", back_populates="announcements")

class Document(Base):
    __tablename__ = "documents"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    filename = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), default="pdf")  # pdf, txt, docx
    file_size = Column(Integer, default=0)
    summary = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    due_datetime = Column(DateTime, nullable=False)
    recurrence = Column(String(50), default="none")  # none, daily, weekly
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    location = Column(String(100), default="Campus / Virtual")
    event_type = Column(String(50), default="class")  # class, exam, study, personal, assignment
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=True)
    description = Column(Text, default="")

class Email(Base):
    __tablename__ = "emails"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender = Column(String(100), nullable=False)
    sender_name = Column(String(100), nullable=False)
    recipient = Column(String(100), default="alex.rivers@university.edu")
    subject = Column(String(250), nullable=False)
    body = Column(Text, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    has_attachments = Column(Boolean, default=False)
    category = Column(String(50), default="academic")  # academic, administrative, announcement

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    due_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    status = Column(String(20), default="todo")      # todo, in_progress, done
    source = Column(String(50), default="user")      # lms, email, user
    created_at = Column(DateTime, default=datetime.utcnow)

class PermissionRequest(Base):
    __tablename__ = "permission_requests"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tool_name = Column(String(100), nullable=False)
    risk_level = Column(String(20), default="SENSITIVE")  # LOW_RISK, SENSITIVE
    parameters_json = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    reason = Column(Text, default="")
    status = Column(String(20), default="PENDING")  # PENDING, APPROVED, DENIED, EXPIRED
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(50), nullable=False)  # TASK_START, TOOL_EXECUTE, PERMISSION_REQUEST, PERMISSION_DECISION, TASK_COMPLETE, ERROR
    tool_name = Column(String(100), nullable=True)
    details = Column(Text, nullable=False)
    status = Column(String(20), default="SUCCESS")   # SUCCESS, FAILED, PENDING, DENIED
    timestamp = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), default="New Study Session")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.timestamp")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    sender = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    steps_json = Column(Text, default="[]")       # List of executed tool step summaries
    files_json = Column(Text, default="[]")       # Associated files/links
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class GeneratedFile(Base):
    __tablename__ = "generated_files"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(200), nullable=False)
    file_type = Column(String(50), default="pptx")  # pptx, pdf, txt, quiz
    file_path = Column(String(500), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
