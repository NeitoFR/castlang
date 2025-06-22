from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, DECIMAL, ForeignKey, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from typing import Optional, List, Dict

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
    
    # Download status: not_downloaded, downloading, downloaded, download_error, extraction_error
    download_status = Column(String(50), default='not_downloaded')
    
    # Transcription status: not_transcribed, transcribing, transcribed, transcription_failed
    transcription_status = Column(String(50), default='not_transcribed')
    
    # Available languages for transcription/translation (JSON array format)
    # Format: ["ja", "en", "fr"]
    available_languages = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    transcriptions = relationship("TranscriptionDB", back_populates="audio_file", cascade="all, delete-orphan")

class TranscriptionDB(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    audio_file_id = Column(Integer, ForeignKey("audio_files.id", ondelete="CASCADE"))
    language = Column(String(10), nullable=False)
    content_type = Column(String(20), nullable=False)  # transcription, translation
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

class TranscriptionRequest(BaseModel):
    audio_file_id: int

class TranscriptionResponse(BaseModel):
    status: str
    message: str
    audio_file_id: int
    transcriptions_count: Optional[int] = None
    error: Optional[str] = None

class TranscriptionStatusResponse(BaseModel):
    audio_file_id: int
    download_status: str
    transcription_status: str
    available_languages: List[str]
    transcriptions_count: Optional[int] = None

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
    download_status: str = 'not_downloaded'
    transcription_status: Optional[str] = 'not_transcribed'
    available_languages: Optional[List[str]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        # Handle migration from old schema
        data = {
            'id': getattr(obj, 'id', None),
            'filename': getattr(obj, 'filename', ''),
            'original_url': getattr(obj, 'original_url', ''),
            'title': getattr(obj, 'title', None),
            'episode_number': getattr(obj, 'episode_number', None),
            'series_name': getattr(obj, 'series_name', None),
            'duration_seconds': getattr(obj, 'duration_seconds', None),
            'file_size_bytes': getattr(obj, 'file_size_bytes', None),
            'file_path': getattr(obj, 'file_path', ''),
            'created_at': getattr(obj, 'created_at', None),
            'updated_at': getattr(obj, 'updated_at', None),
        }
        
        # Handle status migration
        if hasattr(obj, 'download_status') and obj.download_status is not None:
            data['download_status'] = obj.download_status
        elif hasattr(obj, 'status') and obj.status is not None:
            # Migrate old status to download_status
            old_status = obj.status
            if old_status in ['downloaded', 'downloading', 'download_failed', 'file_missing', 'not_downloaded']:
                data['download_status'] = old_status
            else:
                data['download_status'] = 'downloaded'  # Assume downloaded if it was in transcription state
        else:
            data['download_status'] = 'not_downloaded'
        
        # Handle transcription_status
        if hasattr(obj, 'transcription_status') and obj.transcription_status is not None:
            data['transcription_status'] = obj.transcription_status
        elif hasattr(obj, 'status') and obj.status is not None:
            # Migrate old status to transcription_status
            old_status = obj.status
            if old_status in ['transcribed', 'transcribing', 'transcription_failed']:
                data['transcription_status'] = old_status
            else:
                data['transcription_status'] = 'not_transcribed'
        else:
            data['transcription_status'] = 'not_transcribed'
        
        # Handle available_languages
        if hasattr(obj, 'available_languages') and obj.available_languages is not None:
            data['available_languages'] = obj.available_languages
        else:
            data['available_languages'] = []
        
        return cls(**data)

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
    download_status: str
    transcription_status: Optional[str] = 'not_transcribed'
    available_languages: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime
    transcriptions: List[Transcription] = []
    
    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        # Handle migration from old schema
        data = {
            'id': getattr(obj, 'id', 0),
            'filename': getattr(obj, 'filename', ''),
            'original_url': getattr(obj, 'original_url', ''),
            'title': getattr(obj, 'title', None),
            'episode_number': getattr(obj, 'episode_number', None),
            'series_name': getattr(obj, 'series_name', None),
            'duration_seconds': getattr(obj, 'duration_seconds', None),
            'file_size_bytes': getattr(obj, 'file_size_bytes', None),
            'file_path': getattr(obj, 'file_path', ''),
            'created_at': getattr(obj, 'created_at', datetime.utcnow()),
            'updated_at': getattr(obj, 'updated_at', datetime.utcnow()),
            'transcriptions': []
        }
        
        # Handle status migration
        if hasattr(obj, 'download_status') and obj.download_status is not None:
            data['download_status'] = obj.download_status
        elif hasattr(obj, 'status') and obj.status is not None:
            # Migrate old status to download_status
            old_status = obj.status
            if old_status in ['downloaded', 'downloading', 'download_failed', 'file_missing', 'not_downloaded']:
                data['download_status'] = old_status
            else:
                data['download_status'] = 'downloaded'  # Assume downloaded if it was in transcription state
        else:
            data['download_status'] = 'not_downloaded'
        
        # Handle transcription_status
        if hasattr(obj, 'transcription_status') and obj.transcription_status is not None:
            data['transcription_status'] = obj.transcription_status
        elif hasattr(obj, 'status') and obj.status is not None:
            # Migrate old status to transcription_status
            old_status = obj.status
            if old_status in ['transcribed', 'transcribing', 'transcription_failed']:
                data['transcription_status'] = old_status
            else:
                data['transcription_status'] = 'not_transcribed'
        else:
            data['transcription_status'] = 'not_transcribed'
        
        # Handle available_languages
        if hasattr(obj, 'available_languages') and obj.available_languages is not None:
            data['available_languages'] = obj.available_languages
        else:
            data['available_languages'] = []
        
        return cls(**data) 