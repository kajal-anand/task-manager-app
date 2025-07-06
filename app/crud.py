from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import Task, TaskStatus, Tag,TaskPriority
from .schemas import TaskCreate, TaskUpdate
from datetime import datetime
from .ai_service import AIService
import logging

logger = logging.getLogger(__name__)

async def create_task(db: Session, task: TaskCreate):
    """Create a new task with AI-assigned priority and tags."""
    try:
        ai_service = AIService()
        priority = await ai_service.prioritize_task(task.title, task.description or "")
        tags = await ai_service.generate_tags(task.title, task.description or "")
        
        db_task = Task(
            title=task.title,
            description=task.description,
            deadline=task.deadline,
            priority=priority,
            parent_id=task.parent_id
        )
        db.add(db_task)
        
        # Add tags to task
        for tag_name in tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            db_task.tags.append(tag)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        db.rollback()
        raise

async def generate_subtasks(db: Session, task_id: int):
    """Generate sub-tasks for a given task using AI."""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        ai_service = AIService()
        subtask_titles = await ai_service.generate_subtasks(task.title, task.description or "")
        
        subtasks = []
        for title in subtask_titles:
            subtask = Task(
                title=title,
                description=None,
                deadline=task.deadline,
                priority=TaskPriority.LOW,
                parent_id=task_id
            )
            db.add(subtask)
            # Add parent task's tags to sub-task
            for tag in task.tags:
                subtask.tags.append(tag)
            subtasks.append(subtask)
        
        db.commit()
        for subtask in subtasks:
            db.refresh(subtask)
        
        return subtasks
    except Exception as e:
        logger.error(f"Error generating sub-tasks for task {task_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise

def get_tasks(db: Session, status: str = None, priority: str = None, tag: str = None, ordering: str = None):
    """Retrieve all top-level tasks with optional filtering and sorting."""
    try:
        query = db.query(Task).filter(Task.parent_id.is_(None))  # Only top-level tasks
        
        # Update task statuses based on deadline and completion
        for task in db.query(Task).all():  # Update all tasks, including sub-tasks
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
        if tag:
            query = query.join(Task.tags).filter(Tag.name == tag)
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