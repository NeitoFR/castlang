from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse, FileResponse
from typing import List
import os
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from src.models import (
    YouTubeURL, AudioResponse, HealthResponse, AudioFile, AudioFileWithTranscriptions,
    TranscriptionRequest, TranscriptionResponse, TranscriptionStatusResponse, Transcription,
    AudioFileDB
)
from src.services import (
    download_audio, 
    get_downloaded_audio_files, 
    get_audio_file_by_id,
    get_audio_file_by_filename,
    update_audio_file_download_status,
    update_audio_file_transcription_status,
    update_available_languages,
    delete_audio_file,
    get_audio_files_by_series,
    check_all_audio_files_download_status,
    re_download_audio,
    update_audio_file_download_status_from_disk,
    transcribe_audio_file,
    get_transcriptions_for_audio_file,
    get_transcriptions_by_language,
    get_transcriptions_by_content_type,
    get_transcriptions_by_language_and_content_type,
    get_audio_file_with_transcriptions,
    delete_transcriptions_for_audio_file,
    get_transcription_status
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

@router.get("/audio-files/all", response_model=List[AudioFile])
async def list_all_audio_files(db: Session = Depends(get_db)):
    """Get all audio files regardless of status (downloaded, transcribing, transcribed, etc.)"""
    try:
        check_database_connection()
        # Get all audio files without status filtering
        db_audio_files = db.query(AudioFileDB).all()
        return [AudioFile.from_orm(audio_file) for audio_file in db_audio_files]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing all audio files: {e}")
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

@router.put("/audio-files/{audio_file_id}/download-status")
async def update_download_status(audio_file_id: int, status: str, db: Session = Depends(get_db)):
    try:
        check_database_connection()
        audio_file = update_audio_file_download_status(db, audio_file_id, status)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        return {"message": "Download status updated successfully", "audio_file": audio_file}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating download status for audio file {audio_file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/audio-files/{audio_file_id}/transcription-status")
async def update_transcription_status(audio_file_id: int, status: str, db: Session = Depends(get_db)):
    try:
        check_database_connection()
        audio_file = update_audio_file_transcription_status(db, audio_file_id, status)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        return {"message": "Transcription status updated successfully", "audio_file": audio_file}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating transcription status for audio file {audio_file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/audio-files/{audio_file_id}/available-languages")
async def update_languages(audio_file_id: int, languages: List[str], db: Session = Depends(get_db)):
    try:
        check_database_connection()
        audio_file = update_available_languages(db, audio_file_id, languages)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        return {"message": "Available languages updated successfully", "audio_file": audio_file}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating available languages for audio file {audio_file_id}: {e}")
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

@router.post("/audio-files/{audio_file_id}/check-download-status")
async def check_audio_file_download_status(audio_file_id: int, db: Session = Depends(get_db)):
    """Check and update the download status of a specific audio file."""
    try:
        check_database_connection()
        audio_file = update_audio_file_download_status_from_disk(db, audio_file_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        return {"message": "Download status checked successfully", "audio_file": audio_file}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking download status for audio file {audio_file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio-files/check-all-download-status")
async def check_all_audio_files_download_status_endpoint(db: Session = Depends(get_db)):
    """Check and update the download status of all audio files."""
    try:
        check_database_connection()
        audio_files = check_all_audio_files_download_status(db)
        return {"message": "All download statuses checked successfully", "audio_files": audio_files}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking all audio files download status: {e}")
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

# Transcription endpoints
@router.post("/audio-files/{audio_file_id}/transcribe", response_model=TranscriptionResponse)
async def start_transcription(audio_file_id: int, db: Session = Depends(get_db)):
    """Start transcription for an audio file."""
    try:
        check_database_connection()
        
        # Check if audio file exists
        audio_file = get_audio_file_by_id(db, audio_file_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Allow transcription for downloaded files with appropriate transcription status
        if audio_file.download_status != 'downloaded':
            raise HTTPException(
                status_code=400, 
                detail=f"Audio file must be downloaded to transcribe. Current download status: {audio_file.download_status}"
            )
        
        # Allow transcription if not currently transcribing
        if audio_file.transcription_status == 'transcribing':
            raise HTTPException(
                status_code=400, 
                detail="Audio file is currently being transcribed. Please wait for the current transcription to complete."
            )
        
        # If already transcribed or failed, delete existing transcriptions first
        if audio_file.transcription_status in ['transcribed', 'transcription_failed']:
            logger.info(f"Deleting existing transcriptions for audio file {audio_file_id} before re-transcription")
            delete_transcriptions_for_audio_file(audio_file_id, db)
        
        # Start transcription
        result = transcribe_audio_file(audio_file_id, db)
        
        return TranscriptionResponse(
            status="success",
            message="Transcription started successfully",
            audio_file_id=audio_file_id,
            transcriptions_count=result.get("transcriptions_count", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting transcription for audio file {audio_file_id}: {e}")
        return TranscriptionResponse(
            status="error",
            message="Transcription failed",
            audio_file_id=audio_file_id,
            error=str(e)
        )

@router.get("/audio-files/{audio_file_id}/transcription-status", response_model=TranscriptionStatusResponse)
async def get_transcription_status_endpoint(audio_file_id: int, db: Session = Depends(get_db)):
    """Get the transcription status for an audio file."""
    try:
        check_database_connection()
        
        status_info = get_transcription_status(audio_file_id, db)
        if "error" in status_info:
            raise HTTPException(status_code=404, detail=status_info["error"])
        
        return TranscriptionStatusResponse(**status_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transcription status for audio file {audio_file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio-files/{audio_file_id}/transcriptions", response_model=List[Transcription])
async def get_transcriptions(audio_file_id: int, db: Session = Depends(get_db)):
    """Get all transcriptions for an audio file."""
    try:
        check_database_connection()
        
        # Check if audio file exists
        audio_file = get_audio_file_by_id(db, audio_file_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        transcriptions = get_transcriptions_for_audio_file(audio_file_id, db)
        return transcriptions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transcriptions for audio file {audio_file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio-files/{audio_file_id}/transcriptions/{language}", response_model=List[Transcription])
async def get_transcriptions_by_language_endpoint(audio_file_id: int, language: str, db: Session = Depends(get_db)):
    """Get transcriptions for a specific language."""
    try:
        check_database_connection()
        
        # Check if audio file exists
        audio_file = get_audio_file_by_id(db, audio_file_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        transcriptions = get_transcriptions_by_language(audio_file_id, language, db)
        return transcriptions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transcriptions for audio file {audio_file_id} in language {language}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio-files/{audio_file_id}/transcriptions/content-type/{content_type}", response_model=List[Transcription])
async def get_transcriptions_by_content_type_endpoint(audio_file_id: int, content_type: str, db: Session = Depends(get_db)):
    """Get transcriptions for a specific content type (transcription or translation)."""
    try:
        check_database_connection()
        
        # Check if audio file exists
        audio_file = get_audio_file_by_id(db, audio_file_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Validate content type
        if content_type not in ['transcription', 'translation']:
            raise HTTPException(status_code=400, detail="Content type must be 'transcription' or 'translation'")
        
        transcriptions = get_transcriptions_by_content_type(audio_file_id, content_type, db)
        return transcriptions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transcriptions for audio file {audio_file_id} with content type {content_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio-files/{audio_file_id}/transcriptions/{language}/{content_type}", response_model=List[Transcription])
async def get_transcriptions_by_language_and_content_type_endpoint(audio_file_id: int, language: str, content_type: str, db: Session = Depends(get_db)):
    """Get transcriptions for a specific language and content type."""
    try:
        check_database_connection()
        
        # Check if audio file exists
        audio_file = get_audio_file_by_id(db, audio_file_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Validate content type
        if content_type not in ['transcription', 'translation']:
            raise HTTPException(status_code=400, detail="Content type must be 'transcription' or 'translation'")
        
        transcriptions = get_transcriptions_by_language_and_content_type(audio_file_id, language, content_type, db)
        return transcriptions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transcriptions for audio file {audio_file_id} in language {language} with content type {content_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio-files/{audio_file_id}/with-transcriptions", response_model=AudioFileWithTranscriptions)
async def get_audio_file_with_transcriptions_endpoint(audio_file_id: int, db: Session = Depends(get_db)):
    """Get an audio file with all its transcriptions."""
    try:
        check_database_connection()
        
        audio_file_with_transcriptions = get_audio_file_with_transcriptions(audio_file_id, db)
        if not audio_file_with_transcriptions:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return audio_file_with_transcriptions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audio file with transcriptions {audio_file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/audio-files/{audio_file_id}/transcriptions")
async def delete_transcriptions_endpoint(audio_file_id: int, db: Session = Depends(get_db)):
    """Delete all transcriptions for an audio file."""
    try:
        check_database_connection()
        
        # Check if audio file exists
        audio_file = get_audio_file_by_id(db, audio_file_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        success = delete_transcriptions_for_audio_file(audio_file_id, db)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete transcriptions")
        
        return {"message": "Transcriptions deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transcriptions for audio file {audio_file_id}: {e}")
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
        if audio_file.download_status != 'downloaded':
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
        if audio_file.download_status != 'downloaded':
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