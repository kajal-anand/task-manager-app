from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .models import TaskStatus, TaskPriority

class TaskBase(BaseModel):
    title: Optional[str] = None  # Changed to Optional
    description: Optional[str] = None
    deadline: Optional[datetime] = None

class TaskCreate(TaskBase):
    title: str  # Keep title required for task creation

class TaskUpdate(TaskBase):
    completed: Optional[bool] = None

class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    priority: TaskPriority
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        # orm_mode = True
        from_attributes = True