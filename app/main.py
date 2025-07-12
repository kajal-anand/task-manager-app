from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import crud, schemas, database, config, models
from typing import List
import logging

app = FastAPI(title="Task Management API")
config.Config.setup_logging()
logger = logging.getLogger(__name__)

# Initialize database tables
try:
    models.Base.metadata.create_all(bind=database.engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {str(e)}", exc_info=True)
    raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

#  API Endpoints
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Serve the frontend index page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/tasks/", response_model=schemas.TaskResponse)
async def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    """Create a new task."""
    try:
        return await crud.create_task(db, task)
    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/tasks/", response_model=List[schemas.TaskResponse])
def get_tasks(
    db: Session = Depends(database.get_db),
    status: str = None,
    priority: str = None,
    tag: str = None,
    ordering: str = None
):
    """Retrieve tasks with optional filtering and sorting."""
    try:
        return crud.get_tasks(db, status, priority, tag, ordering)
    except Exception as e:
        logger.error(f"Failed to retrieve tasks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(database.get_db)):
    """Retrieve a single task by ID."""
    try:
        task = crud.get_task(db, task_id)
        return task
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to retrieve task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.patch("/api/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(database.get_db)):
    """Update an existing task."""
    try:
        return crud.update_task(db, task_id, task)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    """Delete a task by ID."""
    try:
        return crud.delete_task(db, task_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")