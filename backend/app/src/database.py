from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import time
from dotenv import load_dotenv
from src.models import Base
from sqlalchemy.exc import OperationalError

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
        except OperationalError:
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                return False
    return False

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

def migrate_existing_records():
    """Migrate existing records to have the new status fields."""
    try:
        with engine.connect() as connection:
            # Check if the new columns exist
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'audio_files' 
                AND column_name IN ('download_status', 'transcription_status', 'available_languages')
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            # If new columns don't exist, we need to run the migration first
            if not all(col in existing_columns for col in ['download_status', 'transcription_status', 'available_languages']):
                print("New columns don't exist yet. Please run the alembic migration first.")
                return False
            
            # Check if the old status column exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'audio_files' 
                AND column_name = 'status'
            """))
            has_old_status = result.fetchone() is not None
            
            if has_old_status:
                # Update existing records that have the old status field but not the new ones
                connection.execute(text("""
                    UPDATE audio_files 
                    SET download_status = CASE 
                        WHEN status IN ('downloaded', 'downloading', 'download_failed', 'file_missing', 'not_downloaded') 
                        THEN status 
                        ELSE 'downloaded'
                    END,
                    transcription_status = CASE 
                        WHEN status IN ('transcribed', 'transcribing', 'transcription_failed') 
                        THEN status 
                        ELSE 'not_transcribed'
                    END,
                    available_languages = '[]'::json
                    WHERE download_status IS NULL OR transcription_status IS NULL OR available_languages IS NULL
                """))
            else:
                # Database was created with new schema, just ensure all records have proper values
                connection.execute(text("""
                    UPDATE audio_files 
                    SET download_status = 'not_downloaded'
                    WHERE download_status IS NULL
                """))
                
                connection.execute(text("""
                    UPDATE audio_files 
                    SET transcription_status = 'not_transcribed'
                    WHERE transcription_status IS NULL
                """))
                
                connection.execute(text("""
                    UPDATE audio_files 
                    SET available_languages = '[]'::json
                    WHERE available_languages IS NULL
                """))
            
            connection.commit()
            print("Successfully migrated existing records")
            return True
            
    except Exception as e:
        print(f"Error migrating existing records: {e}")
        return False 