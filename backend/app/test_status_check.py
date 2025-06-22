#!/usr/bin/env python3
"""
Test script to verify status checking functionality
"""

import os
import sys
import requests
import time

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_db, wait_for_database
from src.services import check_all_audio_files_download_status, update_audio_file_download_status_from_disk
from src.models import AudioFileDB

def test_status_checking():
    """Test the status checking functionality"""
    print("Testing status checking functionality...")
    
    # Wait for database
    if not wait_for_database():
        print("❌ Database not available")
        return False
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check all audio files status
        print("Checking all audio files status...")
        audio_files = check_all_audio_files_download_status(db)
        
        print(f"Found {len(audio_files)} audio files:")
        for audio_file in audio_files:
            print(f"  - {audio_file.title} ({audio_file.filename}): download_status={audio_file.download_status}, transcription_status={audio_file.transcription_status}")
        
        # Test individual file status check
        if audio_files:
            first_file = audio_files[0]
            print(f"\nTesting individual status check for: {first_file.title}")
            updated_file = update_audio_file_download_status_from_disk(db, first_file.id)
            if updated_file:
                print(f"  Download status: {updated_file.download_status}")
                print(f"  Transcription status: {updated_file.transcription_status}")
            else:
                print("  ❌ Failed to update status")
        
        print("✅ Status checking test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error during status checking test: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_status_checking() 