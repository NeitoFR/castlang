from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from typing import Optional, List

# SQLAlchemy Base
Base = declarative_base()

# SQLAlchemy Database Models
class AudioFileDB(Base):
    __tablename__ = "audio_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_url = Column(Text, nullable=False)
    title = Column(String(500))
    episode_number = Column(Integer)
    series_name = Column(String(255))
    duration_seconds = Column(Integer)
    file_size_bytes = Column(BigInteger)
    file_path = Column(String(500), nullable=False)
    status = Column(String(50), default='not_downloaded')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    transcriptions = relationship("TranscriptionDB", back_populates="audio_file", cascade="all, delete-orphan")

class TranscriptionDB(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    audio_file_id = Column(Integer, ForeignKey("audio_files.id", ondelete="CASCADE"))
    language = Column(String(10), nullable=False)
    content_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    confidence_score = Column(DECIMAL(3, 2))
    start_time_seconds = Column(DECIMAL(10, 3))
    end_time_seconds = Column(DECIMAL(10, 3))
    segment_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    audio_file = relationship("AudioFileDB", back_populates="transcriptions")

# Pydantic Models for API
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
    id: Optional[int] = None
    filename: str
    original_url: str
    title: Optional[str] = None
    episode_number: Optional[int] = None
    series_name: Optional[str] = None
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None
    file_path: str
    status: str = 'not_downloaded'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Transcription(BaseModel):
    id: Optional[int] = None
    audio_file_id: int
    language: str
    content_type: str
    content: str
    confidence_score: Optional[float] = None
    start_time_seconds: Optional[float] = None
    end_time_seconds: Optional[float] = None
    segment_order: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AudioFileWithTranscriptions(BaseModel):
    id: int
    filename: str
    original_url: str
    title: Optional[str] = None
    episode_number: Optional[int] = None
    series_name: Optional[str] = None
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None
    file_path: str
    status: str
    created_at: datetime
    updated_at: datetime
    transcriptions: List[Transcription] = []
    
    class Config:
        from_attributes = True 