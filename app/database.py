from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import Config
import logging

logger = logging.getLogger(__name__)

try:
    # 1. Create SQLAlchemy Engine
    engine = create_engine(
        Config.DATABASE_URL,
        connect_args={"check_same_thread": False}  # SQLite specific -> required only for SQLite to allow multi-threaded access in FastAPI.
    )
    # SessionLocal is a factory to create database sessions (Session) for each request.
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base() # Declarative Base, a class that all your models (Task, Tag) will inherit from.
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
    raise

def get_db():
    """Dependency to get database session."""
    db = SessionLocal() # Creates a new DB session for the request
    try:
        yield db  # Gives this session to the route handler
    finally:
        db.close()  # After the request, the session is closed (preventing connection leaks) , So you don't have to manage session creation and closing man
