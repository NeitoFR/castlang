from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import tempfile
from pathlib import Path

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class YouTubeURL(BaseModel):
    url: str

@app.post("/extract-audio")
async def extract_audio(youtube_url: YouTubeURL):
    try:
        # Create a temporary directory to store the audio file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            }

            # Download and extract audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url.url, download=True)
                audio_file = list(Path(temp_dir).glob("*.mp3"))[0]
                
                # Read the audio file
                with open(audio_file, "rb") as f:
                    audio_data = f.read()

                return {
                    "title": info.get("title", "Unknown Title"),
                    "audio_data": audio_data,
                    "content_type": "audio/mpeg"
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 