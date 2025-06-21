from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse, FileResponse
from typing import List
import os
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from src.models import YouTubeURL, AudioResponse, HealthResponse, AudioFile, AudioFileWithTranscriptions
from src.services import (
    download_audio, 
    get_downloaded_audio_files, 
    get_audio_file_by_id,
    get_audio_file_by_filename,
    update_audio_file_status,
    delete_audio_file,
    get_audio_files_by_series,
    check_all_audio_files_status,
    re_download_audio,
    update_audio_file_status_from_disk
)
from src.database import get_db, wait_for_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def check_database_connection():
    """Check if database is available and raise appropriate error if not."""
    if not wait_for_database(max_retries=1, retry_interval=1):
        raise HTTPException(
            status_code=503, 
            detail="Database is not available. Please ensure PostgreSQL is running."
        )

@router.post("/extract-audio", response_model=AudioResponse)
async def extract_audio(youtube_url: YouTubeURL, db: Session = Depends(get_db)):
    try:
        check_database_connection()
        audio_file = download_audio(youtube_url.url, db)
        return AudioResponse(
            status="success",
            message="Download successful",
            filename=audio_file.filename,
            path=audio_file.file_path
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")

@router.get("/audio-files", response_model=List[AudioFile])
async def list_audio_files(db: Session = Depends(get_db)):
    try:
        check_database_connection()
        return get_downloaded_audio_files(db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing audio files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio-files/{audio_file_id}", response_model=AudioFile)
async def get_audio_file(audio_file_id: int, db: Session = Depends(get_db)):
    try:
        check_database_connection()
        audio_file = get_audio_file_by_id(db, audio_file_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        return audio_file
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audio file {audio_file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio-files/series/{series_name}", response_model=List[AudioFile])
async def get_audio_files_by_series_name(series_name: str, db: Session = Depends(get_db)):
    try:
        check_database_connection()
        return get_audio_files_by_series(db, series_name)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audio files for series {series_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/audio-files/{audio_file_id}/status")
async def update_status(audio_file_id: int, status: str, db: Session = Depends(get_db)):
    try:
        check_database_connection()
        audio_file = update_audio_file_status(db, audio_file_id, status)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        return {"message": "Status updated successfully", "audio_file": audio_file}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating status for audio file {audio_file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/audio-files/{audio_file_id}")
async def remove_audio_file(audio_file_id: int, db: Session = Depends(get_db)):
    try:
        check_database_connection()
        success = delete_audio_file(db, audio_file_id)
        if not success:
            raise HTTPException(status_code=404, detail="Audio file not found")
        return {"message": "Audio file deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting audio file {audio_file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio-files/{audio_file_id}/check-status")
async def check_audio_file_status(audio_file_id: int, db: Session = Depends(get_db)):
    """Check and update the status of a specific audio file."""
    try:
        check_database_connection()
        audio_file = update_audio_file_status_from_disk(db, audio_file_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        return {"message": "Status checked successfully", "audio_file": audio_file}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking status for audio file {audio_file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio-files/check-all-status")
async def check_all_audio_files_status_endpoint(db: Session = Depends(get_db)):
    """Check and update the status of all audio files."""
    try:
        check_database_connection()
        audio_files = check_all_audio_files_status(db)
        return {"message": "All statuses checked successfully", "audio_files": audio_files}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking all audio files status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio-files/{audio_file_id}/re-download")
async def re_download_audio_file(audio_file_id: int, db: Session = Depends(get_db)):
    """Re-download an audio file using its original URL."""
    try:
        check_database_connection()
        audio_file = re_download_audio(audio_file_id, db)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        return {
            "message": "Audio file re-downloaded successfully", 
            "audio_file": audio_file
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error re-downloading audio file {audio_file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream/{filename}")
async def stream_audio(filename: str, request: Request, db: Session = Depends(get_db)):
    """Stream audio file with support for range requests (seeking)"""
    try:
        check_database_connection()
        # Get audio file from database
        audio_file = get_audio_file_by_filename(db, filename)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Check if file is actually available
        if audio_file.status != 'downloaded':
            raise HTTPException(status_code=404, detail="Audio file not available for streaming")
        
        file_path = Path(audio_file.file_path)
        
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Check if this is a range request
        range_header = request.headers.get("range")
        
        if range_header:
            # Parse range header (e.g., "bytes=0-1023")
            try:
                range_match = range_header.replace("bytes=", "").split("-")
                start = int(range_match[0]) if range_match[0] else 0
                end = int(range_match[1]) if range_match[1] else file_size - 1
                
                if start >= file_size:
                    raise HTTPException(status_code=416, detail="Range Not Satisfiable")
                
                if end >= file_size:
                    end = file_size - 1
                    
                chunk_size = end - start + 1
                
                def generate_chunk():
                    with open(file_path, "rb") as file:
                        file.seek(start)
                        remaining = chunk_size
                        while remaining > 0:
                            read_size = min(remaining, 8192)  # 8KB chunks
                            chunk = file.read(read_size)
                            if not chunk:
                                break
                            remaining -= len(chunk)
                            yield chunk
                
                headers = {
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(chunk_size),
                    "Content-Type": "audio/mpeg",
                }
                
                return StreamingResponse(
                    generate_chunk(),
                    status_code=206,
                    headers=headers
                )
            except (ValueError, IndexError):
                # Invalid range header, serve full file
                pass
        
        # Serve full file
        def generate_file():
            with open(file_path, "rb") as file:
                while True:
                    chunk = file.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    yield chunk
        
        headers = {
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
            "Content-Type": "audio/mpeg",
        }
        
        return StreamingResponse(generate_file(), headers=headers)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error streaming audio file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_audio_file(filename: str, db: Session = Depends(get_db)):
    """Download audio file (for backward compatibility)"""
    try:
        check_database_connection()
        # Get audio file from database
        audio_file = get_audio_file_by_filename(db, filename)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Check if file is actually available
        if audio_file.status != 'downloaded':
            raise HTTPException(status_code=404, detail="Audio file not available for download")
        
        file_path = Path(audio_file.file_path)
        
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            file_path,
            media_type="audio/mpeg",
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading audio file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 