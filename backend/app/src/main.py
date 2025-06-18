from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import tempfile
from pathlib import Path
import re

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create downloads directory if it doesn't exist
DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)

class YouTubeURL(BaseModel):
    url: str

def sanitize_filename(filename: str) -> str:
    # Replace non-ASCII characters with their closest ASCII equivalent or remove them
    # Remove any characters that aren't alphanumeric, spaces, or basic punctuation
    sanitized = re.sub(r'[^\x00-\x7F]+', '', filename)
    # Replace spaces and other problematic characters with underscores
    sanitized = re.sub(r'[^\w\-\.]', '_', sanitized)
    # Ensure the filename isn't too long
    return sanitized[:100]

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
                
                # Create a sanitized filename for the downloads folder
                safe_filename = sanitize_filename(info.get("title", "audio"))
                destination_path = DOWNLOADS_DIR / f"{safe_filename}.mp3"
                
                # Copy the file to the downloads directory
                with open(audio_file, "rb") as src, open(destination_path, "wb") as dst:
                    dst.write(src.read())

                return {
                    "status": "success",
                    "message": "Download successful",
                    "filename": f"{safe_filename}.mp3",
                    "path": str(destination_path)
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 