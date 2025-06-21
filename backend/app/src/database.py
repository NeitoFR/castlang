from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import time
from dotenv import load_dotenv
from src.models import Base

# Load environment variables from .env file
load_dotenv()

# Database configuration with granular environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "castlang")
DB_USER = os.getenv("DB_USER", "castlang")
DB_PASSWORD = os.getenv("DB_PASSWORD", "castlang")

# Construct DATABASE_URL from individual components
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Fallback to DATABASE_URL if provided directly
if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    echo=os.getenv("DB_ECHO", "false").lower() == "true"  # SQL debugging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def wait_for_database(max_retries=30, retry_interval=2):
    """
    Wait for database to be available.
    
    Args:
        max_retries (int): Maximum number of retry attempts
        retry_interval (int): Seconds to wait between retries
    
    Returns:
        bool: True if database is available, False otherwise
    """
    for attempt in range(max_retries):
        try:
            # Try to create a connection
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                connection.commit()
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                return False
    return False

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine) 