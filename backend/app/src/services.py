import yt_dlp
import os
import tempfile
from pathlib import Path
import re
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models import AudioFile, AudioFileDB, TranscriptionDB
from src.database import get_db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment variables
DOWNLOADS_DIR = Path(os.getenv("DOWNLOADS_DIR", "downloads"))
DOWNLOADS_DIR.mkdir(exist_ok=True)

# yt-dlp configuration
AUDIO_FORMAT = os.getenv("AUDIO_FORMAT", "bestaudio/best")
AUDIO_CODEC = os.getenv("AUDIO_CODEC", "mp3")
AUDIO_QUALITY = os.getenv("AUDIO_QUALITY", "192")

def sanitize_filename(filename: str) -> str:
    # Replace non-ASCII characters with their closest ASCII equivalent or remove them
    # Remove any characters that aren't alphanumeric, spaces, or basic punctuation
    sanitized = re.sub(r'[^\x00-\x7F]+', '', filename)
    # Replace spaces and other problematic characters with underscores
    sanitized = re.sub(r'[^\w\-\.]', '_', sanitized)
    # Ensure the filename isn't too long
    return sanitized[:100]

def check_file_exists(file_path: str) -> bool:
    """Check if the audio file exists on disk."""
    return Path(file_path).exists() and Path(file_path).is_file()

def update_audio_file_status_from_disk(db: Session, audio_file_id: int) -> Optional[AudioFile]:
    """Update audio file status based on whether the file exists on disk."""
    db_audio_file = db.query(AudioFileDB).filter(AudioFileDB.id == audio_file_id).first()
    if db_audio_file:
        file_exists = check_file_exists(db_audio_file.file_path)
        new_status = 'downloaded' if file_exists else 'file_missing'
        
        if db_audio_file.status != new_status:
            db_audio_file.status = new_status
            db.commit()
            db.refresh(db_audio_file)
        
        return AudioFile.from_orm(db_audio_file)
    return None

def check_all_audio_files_status(db: Session) -> List[AudioFile]:
    """Check and update status of all audio files based on disk presence."""
    db_audio_files = db.query(AudioFileDB).all()
    updated_files = []
    
    for db_audio_file in db_audio_files:
        file_exists = check_file_exists(db_audio_file.file_path)
        new_status = 'downloaded' if file_exists else 'file_missing'
        
        if db_audio_file.status != new_status:
            db_audio_file.status = new_status
        
        updated_files.append(AudioFile.from_orm(db_audio_file))
    
    db.commit()
    return updated_files

def re_download_audio(audio_file_id: int, db: Session) -> Optional[AudioFile]:
    """Re-download an audio file using its original URL."""
    db_audio_file = db.query(AudioFileDB).filter(AudioFileDB.id == audio_file_id).first()
    if not db_audio_file:
        return None
    
    try:
        # Update status to downloading
        db_audio_file.status = 'downloading'
        db.commit()
        
        # Download the audio file and update the existing record
        audio_file = download_audio(db_audio_file.original_url, db, existing_audio_file=db_audio_file)
        
        if audio_file:
            return audio_file
        
    except Exception as e:
        # Update status to failed
        db_audio_file.status = 'download_failed'
        db.commit()
        raise e
    
    return None

def download_audio(url: str, db: Session, existing_audio_file: Optional[AudioFileDB] = None) -> AudioFile:
    # Create a temporary directory to store the audio file
    with tempfile.TemporaryDirectory() as temp_dir:
        # Configure yt-dlp options
        ydl_opts = {
            'format': AUDIO_FORMAT,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': AUDIO_CODEC,
                'preferredquality': AUDIO_QUALITY,
            }],
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        }

        # Download and extract audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = list(Path(temp_dir).glob("*.mp3"))[0]
            
            # Create a sanitized filename for the downloads folder
            safe_filename = sanitize_filename(info.get("title", "audio"))
            destination_path = DOWNLOADS_DIR / f"{safe_filename}.mp3"
            
            # Copy the file to the downloads directory
            with open(audio_file, "rb") as src, open(destination_path, "wb") as dst:
                dst.write(src.read())

            # Get file size
            file_size = destination_path.stat().st_size
            
            if existing_audio_file:
                # Update existing record
                existing_audio_file.filename = f"{safe_filename}.mp3"
                existing_audio_file.title = info.get("title")
                existing_audio_file.episode_number = info.get("episode_number")
                existing_audio_file.series_name = info.get("series")
                existing_audio_file.duration_seconds = info.get("duration")
                existing_audio_file.file_size_bytes = file_size
                existing_audio_file.file_path = str(destination_path)
                existing_audio_file.status = 'downloaded'
                
                db.commit()
                db.refresh(existing_audio_file)
                return AudioFile.from_orm(existing_audio_file)
            else:
                # Create new database record
                db_audio_file = AudioFileDB(
                    filename=f"{safe_filename}.mp3",
                    original_url=url,
                    title=info.get("title"),
                    episode_number=info.get("episode_number"),
                    series_name=info.get("series"),
                    duration_seconds=info.get("duration"),
                    file_size_bytes=file_size,
                    file_path=str(destination_path),
                    status='downloaded'
                )
                
                db.add(db_audio_file)
                db.commit()
                db.refresh(db_audio_file)

                return AudioFile.from_orm(db_audio_file)

def get_downloaded_audio_files(db: Session) -> List[AudioFile]:
    # First check and update all file statuses
    check_all_audio_files_status(db)
    
    # Then return the updated list
    db_audio_files = db.query(AudioFileDB).all()
    return [AudioFile.from_orm(audio_file) for audio_file in db_audio_files]

def get_audio_file_by_id(db: Session, audio_file_id: int) -> Optional[AudioFile]:
    # Check and update status before returning
    updated_file = update_audio_file_status_from_disk(db, audio_file_id)
    if updated_file:
        return updated_file
    
    db_audio_file = db.query(AudioFileDB).filter(AudioFileDB.id == audio_file_id).first()
    if db_audio_file:
        return AudioFile.from_orm(db_audio_file)
    return None

def get_audio_file_by_filename(db: Session, filename: str) -> Optional[AudioFile]:
    db_audio_file = db.query(AudioFileDB).filter(AudioFileDB.filename == filename).first()
    if db_audio_file:
        # Check and update status
        update_audio_file_status_from_disk(db, db_audio_file.id)
        return AudioFile.from_orm(db_audio_file)
    return None

def update_audio_file_status(db: Session, audio_file_id: int, status: str) -> Optional[AudioFile]:
    db_audio_file = db.query(AudioFileDB).filter(AudioFileDB.id == audio_file_id).first()
    if db_audio_file:
        db_audio_file.status = status
        db.commit()
        db.refresh(db_audio_file)
        return AudioFile.from_orm(db_audio_file)
    return None

def delete_audio_file(db: Session, audio_file_id: int) -> bool:
    db_audio_file = db.query(AudioFileDB).filter(AudioFileDB.id == audio_file_id).first()
    if db_audio_file:
        # Delete the physical file
        file_path = Path(db_audio_file.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # Delete from database
        db.delete(db_audio_file)
        db.commit()
        return True
    return False

def get_audio_files_by_series(db: Session, series_name: str) -> List[AudioFile]:
    # Check and update all file statuses first
    check_all_audio_files_status(db)
    
    db_audio_files = db.query(AudioFileDB).filter(AudioFileDB.series_name == series_name).order_by(AudioFileDB.episode_number).all()
    return [AudioFile.from_orm(audio_file) for audio_file in db_audio_files] 