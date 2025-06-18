from fastapi import APIRouter, HTTPException
from typing import List
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