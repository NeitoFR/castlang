import os
import requests
import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.models import AudioFileDB, TranscriptionDB
from src.database import get_db
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gladia API configuration
GLADIA_API_KEY = os.getenv("GLADIA_API_KEY")
GLADIA_UPLOAD_URL = "https://api.gladia.io/v2/upload/"
GLADIA_TRANSCRIPTION_URL = "https://api.gladia.io/v2/pre-recorded/"

if not GLADIA_API_KEY:
    logger.warning("GLADIA_API_KEY not found in environment variables")

class TranscriptionService:
    def __init__(self):
        self.api_key = GLADIA_API_KEY
        self.upload_url = GLADIA_UPLOAD_URL
        self.transcription_url = GLADIA_TRANSCRIPTION_URL
    
    def _upload_audio_file(self, file_path: str) -> str:
        """Upload audio file to Gladia and return the audio_url."""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Audio file not found at {file_path}")
            
            # Get file extension
            file_name, file_extension = os.path.splitext(file_path)
            
            # Prepare headers
            headers = {
                "x-gladia-key": self.api_key,
                "accept": "application/json",
            }
            
            # Read file content
            with open(file_path, "rb") as f:
                file_content = f.read()
            
            # Prepare files for upload
            files = [("audio", (os.path.basename(file_path), file_content, "audio/" + file_extension[1:]))]
            
            logger.info(f"Uploading file {file_path} to Gladia...")
            response = requests.post(
                self.upload_url,
                headers=headers,
                files=files
            )
            
            if response.status_code != 200:
                logger.error(f"Upload failed: {response.status_code} - {response.text}")
                raise Exception(f"Upload failed: {response.status_code} - {response.text}")
            
            upload_response = response.json()
            logger.info(f"Upload response: {upload_response}")
            
            audio_url = upload_response.get("audio_url")
            if not audio_url:
                raise Exception("No audio_url returned from upload")
            
            return audio_url
            
        except Exception as e:
            logger.error(f"Error uploading audio file {file_path}: {e}")
            raise
    
    def _start_transcription(self, audio_url: str) -> Dict[str, Any]:
        """Start transcription process and return transcription info."""
        try:
            # Prepare headers
            headers = {
                "x-gladia-key": self.api_key,
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            
            # Prepare transcription request data with translation enabled
            data = {
                "audio_url": audio_url,
                "diarization": True,
                "diarization_config": {
                    "number_of_speakers": 1,
                    "min_speakers": 1,
                    "max_speakers": 3
                },
                "detect_language": True,
                "enable_code_switching": True,
                "translation": True,  # Enable translation
                "translation_config": {
                    "target_languages": ["fr", "en"]  # French and English translations
                },
                "subtitles": True,    # Enable subtitles
                "subtitles_config": {
                    "formats": ["srt"]
                }
            }
            
            logger.info("Sending transcription request to Gladia API...")
            response = requests.post(
                self.transcription_url,
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                logger.error(f"Transcription request failed: {response.status_code} - {response.text}")
                raise Exception(f"Transcription request failed: {response.status_code} - {response.text}")
            
            post_response = response.json()
            logger.info(f"Transcription request response: {post_response}")
            
            return post_response
            
        except Exception as e:
            logger.error(f"Error starting transcription: {e}")
            raise
    
    def _poll_transcription_result(self, result_url: str) -> Dict[str, Any]:
        """Poll for transcription results until completion."""
        try:
            headers = {
                "x-gladia-key": self.api_key,
                "accept": "application/json",
            }
            
            max_attempts = 300  # 5 minutes with 1-second intervals
            attempts = 0
            
            while attempts < max_attempts:
                logger.info(f"Polling for results... (attempt {attempts + 1})")
                
                response = requests.get(result_url, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"Polling failed: {response.status_code} - {response.text}")
                    raise Exception(f"Polling failed: {response.status_code} - {response.text}")
                
                poll_response = response.json()
                status = poll_response.get("status")
                
                if status == "done":
                    logger.info("Transcription completed successfully")
                    return poll_response
                elif status == "error":
                    logger.error("Transcription failed")
                    logger.error(poll_response)
                    raise Exception("Transcription failed")
                else:
                    logger.info(f"Transcription status: {status}")
                    time.sleep(1)
                    attempts += 1
            
            raise Exception("Transcription timed out")
            
        except Exception as e:
            logger.error(f"Error polling transcription result: {e}")
            raise
    
    def transcribe_audio_file(self, audio_file_id: int, db: Session) -> Dict[str, Any]:
        """Transcribe an audio file using Gladia API with the correct workflow."""
        if not self.api_key:
            raise ValueError("GLADIA_API_KEY is required for transcription")
        
        # Get audio file from database
        audio_file = db.query(AudioFileDB).filter(AudioFileDB.id == audio_file_id).first()
        if not audio_file:
            raise ValueError(f"Audio file with ID {audio_file_id} not found")
        
        # Check if file exists
        if not os.path.exists(audio_file.file_path):
            raise FileNotFoundError(f"Audio file not found at {audio_file.file_path}")
        
        # Update status to transcribing
        audio_file.status = 'transcribing'
        db.commit()
        
        try:
            # Step 1: Upload the audio file
            audio_url = self._upload_audio_file(audio_file.file_path)
            
            # Step 2: Start transcription
            transcription_info = self._start_transcription(audio_url)
            result_url = transcription_info.get("result_url")
            
            if not result_url:
                raise Exception("No result_url returned from transcription request")
            
            # Step 3: Poll for results
            result = self._poll_transcription_result(result_url)
            
            logger.info(f"Transcription completed for audio file {audio_file_id}")
            
            # Save transcriptions to database
            transcriptions = self._save_transcriptions_to_db(result, audio_file_id, db)
            
            # Update audio file status
            audio_file.status = 'transcribed'
            db.commit()
            
            return {
                "status": "success",
                "audio_file_id": audio_file_id,
                "transcriptions_count": len(transcriptions),
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio file {audio_file_id}: {e}")
            audio_file.status = 'transcription_failed'
            db.commit()
            raise
    
    def _save_transcriptions_to_db(self, api_result: Dict[str, Any], audio_file_id: int, db: Session) -> List[TranscriptionDB]:
        """Save transcription results and translations to database."""
        transcriptions = []
        
        try:
            # Extract transcription data from API response
            # The structure depends on the Gladia API response format
            if 'result' in api_result:
                result_data = api_result['result']
                
                # Handle different possible response structures
                if 'prediction' in result_data:
                    # New API format
                    segments = result_data['prediction'].get('segments', [])
                elif 'segments' in result_data:
                    # Alternative format
                    segments = result_data['segments']
                else:
                    # Fallback: try to find segments in the result
                    segments = result_data.get('segments', [])
                
                for i, segment in enumerate(segments):
                    # Get the transcription text
                    transcription_text = segment.get('transcription', '')
                    if not transcription_text.strip():
                        continue
                    
                    # Get timing information
                    start_time = segment.get('start', 0.0)
                    end_time = segment.get('end', 0.0)
                    
                    # Get confidence score if available
                    confidence = segment.get('confidence', None)
                    
                    # Detect language (default to Japanese for this use case)
                    detected_language = segment.get('language', 'ja')
                    
                    # Create transcription record
                    transcription = TranscriptionDB(
                        audio_file_id=audio_file_id,
                        language=detected_language,
                        content_type='transcription',
                        content=transcription_text,
                        confidence_score=confidence,
                        start_time_seconds=start_time,
                        end_time_seconds=end_time,
                        segment_order=i + 1
                    )
                    
                    db.add(transcription)
                    transcriptions.append(transcription)
                    
                    # Handle translations if available
                    translations = segment.get('translations', {})
                    
                    # Save English translation
                    if 'en' in translations:
                        en_translation = translations['en']
                        if en_translation.strip():
                            en_transcription = TranscriptionDB(
                                audio_file_id=audio_file_id,
                                language='en',
                                content_type='translation',
                                content=en_translation,
                                confidence_score=confidence,
                                start_time_seconds=start_time,
                                end_time_seconds=end_time,
                                segment_order=i + 1
                            )
                            db.add(en_transcription)
                            transcriptions.append(en_transcription)
                    
                    # Save French translation
                    if 'fr' in translations:
                        fr_translation = translations['fr']
                        if fr_translation.strip():
                            fr_transcription = TranscriptionDB(
                                audio_file_id=audio_file_id,
                                language='fr',
                                content_type='translation',
                                content=fr_translation,
                                confidence_score=confidence,
                                start_time_seconds=start_time,
                                end_time_seconds=end_time,
                                segment_order=i + 1
                            )
                            db.add(fr_transcription)
                            transcriptions.append(fr_transcription)
                
                # Commit all transcriptions and translations
                db.commit()
                logger.info(f"Saved {len(transcriptions)} transcription and translation segments to database")
                
        except Exception as e:
            logger.error(f"Error saving transcriptions to database: {e}")
            db.rollback()
            raise
        
        return transcriptions
    
    def get_transcriptions_for_audio_file(self, audio_file_id: int, db: Session) -> List[TranscriptionDB]:
        """Get all transcriptions for an audio file."""
        return db.query(TranscriptionDB).filter(
            TranscriptionDB.audio_file_id == audio_file_id
        ).order_by(TranscriptionDB.segment_order).all()
    
    def get_transcriptions_by_language(self, audio_file_id: int, language: str, db: Session) -> List[TranscriptionDB]:
        """Get transcriptions for a specific language."""
        return db.query(TranscriptionDB).filter(
            TranscriptionDB.audio_file_id == audio_file_id,
            TranscriptionDB.language == language
        ).order_by(TranscriptionDB.segment_order).all()
    
    def get_transcriptions_by_content_type(self, audio_file_id: int, content_type: str, db: Session) -> List[TranscriptionDB]:
        """Get transcriptions for a specific content type (transcription or translation)."""
        return db.query(TranscriptionDB).filter(
            TranscriptionDB.audio_file_id == audio_file_id,
            TranscriptionDB.content_type == content_type
        ).order_by(TranscriptionDB.segment_order).all()
    
    def get_transcriptions_by_language_and_content_type(self, audio_file_id: int, language: str, content_type: str, db: Session) -> List[TranscriptionDB]:
        """Get transcriptions for a specific language and content type."""
        return db.query(TranscriptionDB).filter(
            TranscriptionDB.audio_file_id == audio_file_id,
            TranscriptionDB.language == language,
            TranscriptionDB.content_type == content_type
        ).order_by(TranscriptionDB.segment_order).all()
    
    def delete_transcriptions_for_audio_file(self, audio_file_id: int, db: Session) -> bool:
        """Delete all transcriptions for an audio file."""
        try:
            deleted_count = db.query(TranscriptionDB).filter(
                TranscriptionDB.audio_file_id == audio_file_id
            ).delete()
            db.commit()
            logger.info(f"Deleted {deleted_count} transcriptions for audio file {audio_file_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting transcriptions: {e}")
            db.rollback()
            return False

# Global transcription service instance
transcription_service = TranscriptionService() 