from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
import enum

class TaskStatus(enum.Enum):
    UPCOMING = "upcoming"
    COMPLETED = "completed"
    MISSED = "missed"

class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Many-to-Many relationship table
task_tags = Table(
    'task_tags',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.UPCOMING)
    priority = Column(Enum(TaskPriority), default=TaskPriority.LOW)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    tasks = relationship("Task", secondary=task_tags, back_populates="tags")