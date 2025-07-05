from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .models import TaskStatus, TaskPriority

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int

    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None

class TaskCreate(TaskBase):
    title: str

class TaskUpdate(TaskBase):
    completed: Optional[bool] = None

class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    priority: TaskPriority
    completed: bool
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        # orm_mode = True
        from_attributes = True