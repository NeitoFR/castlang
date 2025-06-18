from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse
from typing import List
import os
from pathlib import Path
from src.models import YouTubeURL, AudioResponse, HealthResponse, AudioFile
from src.services import download_audio, get_downloaded_audio_files

router = APIRouter()

@router.post("/extract-audio", response_model=AudioResponse)
async def extract_audio(youtube_url: YouTubeURL):
    try:
        audio_file = download_audio(youtube_url.url)
        return AudioResponse(
            status="success",
            message="Download successful",
            filename=audio_file.filename,
            path=audio_file.path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")

@router.get("/audio-files", response_model=List[AudioFile])
async def list_audio_files():
    try:
        return get_downloaded_audio_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream/{filename}")
async def stream_audio(filename: str, request: Request):
    """Stream audio file with support for range requests (seeking)"""
    downloads_dir = Path("downloads")
    file_path = downloads_dir / filename
    
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

@router.get("/download/{filename}")
async def download_audio_file(filename: str):
    """Download audio file (for backward compatibility)"""
    downloads_dir = Path("downloads")
    file_path = downloads_dir / filename
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    ) 