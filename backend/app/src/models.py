from pydantic import BaseModel

class YouTubeURL(BaseModel):
    url: str

class AudioResponse(BaseModel):
    status: str
    message: str
    filename: str
    path: str

class HealthResponse(BaseModel):
    status: str

class AudioFile(BaseModel):
    filename: str
    path: str 