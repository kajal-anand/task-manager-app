from sqlalchemy.orm import Session
from .models import Task, TaskStatus
from .schemas import TaskCreate, TaskUpdate
from datetime import datetime
from .ai_service import AIService
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

async def create_task(db: Session, task: TaskCreate):
    """Create a new task with AI-assigned priority."""
    try:
        ai_service = AIService()
        priority = await ai_service.prioritize_task(task.title, task.description or "")
        
        db_task = Task(
            title=task.title,
            description=task.description,
            deadline=task.deadline,
            priority=priority
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        db.rollback()
        raise

def get_tasks(db: Session, status: str = None, priority: str = None, ordering: str = None):
    """Retrieve tasks with optional filtering and sorting."""
    try:
        query = db.query(Task)
        
        # Update task statuses based on deadline and completion
        for task in query.all():
            if task.completed:
                task.status = TaskStatus.COMPLETED
            elif task.deadline and task.deadline < datetime.utcnow():
                task.status = TaskStatus.MISSED
            else:
                task.status = TaskStatus.UPCOMING
        
        if status:
            query = query.filter(Task.status == TaskStatus(status))
        if priority:
            query = query.filter(Task.priority == priority)
        if ordering:
            if ordering.startswith('-'):
                query = query.order_by(getattr(Task, ordering[1:]).desc())
            else:
                query = query.order_by(getattr(Task, ordering))
                
        db.commit()
        return query.all()
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}", exc_info=True)
        raise

def get_task(db: Session, task_id: int):
    """Retrieve a single task by ID."""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {str(e)}", exc_info=True)
        raise

def update_task(db: Session, task_id: int, task_update: TaskUpdate):
    """Update an existing task."""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        update_data = task_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
            
        if task.completed:
            task.status = TaskStatus.COMPLETED
        elif task.deadline and task.deadline < datetime.utcnow():
            task.status = TaskStatus.MISSED
        else:
            task.status = TaskStatus.UPCOMING
            
        db.commit()
        db.refresh(task)
        return task
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise

def delete_task(db: Session, task_id: int):
    """Delete a task by ID."""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        db.delete(task)
        db.commit()
        return {"message": "Task deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise