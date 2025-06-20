#!/usr/bin/env python3
"""
Test script for the transcription functionality.
This script tests the transcription service and API endpoints using the correct Gladia API workflow.
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
GLADIA_API_KEY = os.getenv("GLADIA_API_KEY")

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_audio_files_list():
    """Test listing audio files."""
    print("Testing audio files list...")
    try:
        response = requests.get(f"{BASE_URL}/audio-files")
        if response.status_code == 200:
            audio_files = response.json()
            print(f"✓ Found {len(audio_files)} audio files")
            return audio_files
        else:
            print(f"✗ Failed to get audio files: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Failed to get audio files: {e}")
        return []

def test_transcription_status(audio_file_id):
    """Test getting transcription status."""
    print(f"Testing transcription status for audio file {audio_file_id}...")
    try:
        response = requests.get(f"{BASE_URL}/audio-files/{audio_file_id}/transcription-status")
        if response.status_code == 200:
            status = response.json()
            print(f"✓ Transcription status: {status['status']}")
            if status.get('transcriptions_count'):
                print(f"  Transcriptions count: {status['transcriptions_count']}")
            return status
        else:
            print(f"✗ Failed to get transcription status: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Failed to get transcription status: {e}")
        return None

def test_start_transcription(audio_file_id):
    """Test starting transcription."""
    print(f"Testing transcription start for audio file {audio_file_id}...")
    print("  Note: This will take several minutes to complete...")
    try:
        response = requests.post(f"{BASE_URL}/audio-files/{audio_file_id}/transcribe")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Transcription started: {result['message']}")
            if result.get('transcriptions_count'):
                print(f"  Transcriptions count: {result['transcriptions_count']}")
            return result
        else:
            print(f"✗ Failed to start transcription: {response.status_code}")
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"  Error: {error_detail}")
            return None
    except Exception as e:
        print(f"✗ Failed to start transcription: {e}")
        return None

def test_get_transcriptions(audio_file_id):
    """Test getting transcriptions."""
    print(f"Testing get transcriptions for audio file {audio_file_id}...")
    try:
        response = requests.get(f"{BASE_URL}/audio-files/{audio_file_id}/transcriptions")
        if response.status_code == 200:
            transcriptions = response.json()
            print(f"✓ Found {len(transcriptions)} transcription segments")
            if transcriptions:
                # Show first transcription
                first = transcriptions[0]
                print(f"  First segment: {first['content'][:50]}...")
                print(f"  Language: {first.get('language', 'unknown')}")
                print(f"  Confidence: {first.get('confidence_score', 'N/A')}")
            return transcriptions
        else:
            print(f"✗ Failed to get transcriptions: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Failed to get transcriptions: {e}")
        return []

def test_get_transcriptions_by_language(audio_file_id, language="ja"):
    """Test getting transcriptions by language."""
    print(f"Testing get transcriptions by language '{language}' for audio file {audio_file_id}...")
    try:
        response = requests.get(f"{BASE_URL}/audio-files/{audio_file_id}/transcriptions/{language}")
        if response.status_code == 200:
            transcriptions = response.json()
            print(f"✓ Found {len(transcriptions)} transcription segments in {language}")
            return transcriptions
        else:
            print(f"✗ Failed to get transcriptions by language: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Failed to get transcriptions by language: {e}")
        return []

def test_audio_file_with_transcriptions(audio_file_id):
    """Test getting audio file with transcriptions."""
    print(f"Testing get audio file with transcriptions for audio file {audio_file_id}...")
    try:
        response = requests.get(f"{BASE_URL}/audio-files/{audio_file_id}/with-transcriptions")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Got audio file with {len(result['transcriptions'])} transcriptions")
            print(f"  Audio file: {result['filename']}")
            print(f"  Status: {result['status']}")
            return result
        else:
            print(f"✗ Failed to get audio file with transcriptions: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Failed to get audio file with transcriptions: {e}")
        return None

def wait_for_transcription_completion(audio_file_id, max_wait_minutes=10):
    """Wait for transcription to complete."""
    print(f"Waiting for transcription to complete (max {max_wait_minutes} minutes)...")
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    while time.time() - start_time < max_wait_seconds:
        status = test_transcription_status(audio_file_id)
        if status and status['status'] == 'transcribed':
            print("✓ Transcription completed!")
            return True
        elif status and status['status'] == 'transcription_failed':
            print("✗ Transcription failed!")
            return False
        
        print("  Still transcribing... waiting 30 seconds")
        time.sleep(30)
    
    print(f"✗ Transcription timed out after {max_wait_minutes} minutes")
    return False

def main():
    """Main test function."""
    print("=== Transcription Service Test (Gladia API v2) ===")
    print()
    
    # Check if Gladia API key is configured
    if not GLADIA_API_KEY:
        print("⚠️  GLADIA_API_KEY not found in environment variables")
        print("   Please set GLADIA_API_KEY in your .env file")
        print("   Get a free API key at https://www.gladia.io/")
        print()
    
    # Test health check
    if not test_health_check():
        print("Server is not running. Please start the server first.")
        return
    
    print()
    
    # Test audio files list
    audio_files = test_audio_files_list()
    if not audio_files:
        print("No audio files found. Please download some audio files first.")
        return
    
    print()
    
    # Find a downloaded audio file
    downloaded_files = [f for f in audio_files if f['status'] == 'downloaded']
    if not downloaded_files:
        print("No downloaded audio files found. Please download some audio files first.")
        return
    
    test_file = downloaded_files[0]
    audio_file_id = test_file['id']
    print(f"Using audio file: {test_file['filename']} (ID: {audio_file_id})")
    print(f"  Duration: {test_file.get('duration_seconds', 'unknown')} seconds")
    print(f"  File size: {test_file.get('file_size_bytes', 'unknown')} bytes")
    print()
    
    # Test transcription status
    status = test_transcription_status(audio_file_id)
    print()
    
    # If not transcribed, try to start transcription
    if status and status['status'] != 'transcribed':
        if status['status'] == 'downloaded':
            print("Starting transcription...")
            result = test_start_transcription(audio_file_id)
            if result:
                print("Transcription started successfully!")
                print("This process will:")
                print("  1. Upload the audio file to Gladia servers")
                print("  2. Start the transcription process")
                print("  3. Poll for results until completion")
                print("  4. Save transcriptions to the database")
                print()
                
                # Wait for completion
                if wait_for_transcription_completion(audio_file_id):
                    print("Transcription completed successfully!")
                else:
                    print("Transcription failed or timed out.")
                    print("You can check the status manually with:")
                    print(f"  curl {BASE_URL}/audio-files/{audio_file_id}/transcription-status")
                    return
            print()
        else:
            print(f"Audio file status is '{status['status']}', skipping transcription test.")
            print()
    
    # Test getting transcriptions (if available)
    if status and status['status'] == 'transcribed':
        transcriptions = test_get_transcriptions(audio_file_id)
        print()
        
        if transcriptions:
            # Test getting transcriptions by language
            test_get_transcriptions_by_language(audio_file_id, "ja")
            print()
            
            # Test getting audio file with transcriptions
            test_audio_file_with_transcriptions(audio_file_id)
            print()
    
    print("=== Test Complete ===")
    print()
    print("API Endpoints tested:")
    print(f"  GET  {BASE_URL}/health")
    print(f"  GET  {BASE_URL}/audio-files")
    print(f"  GET  {BASE_URL}/audio-files/{{id}}/transcription-status")
    print(f"  POST {BASE_URL}/audio-files/{{id}}/transcribe")
    print(f"  GET  {BASE_URL}/audio-files/{{id}}/transcriptions")
    print(f"  GET  {BASE_URL}/audio-files/{{id}}/transcriptions/{{language}}")
    print(f"  GET  {BASE_URL}/audio-files/{{id}}/with-transcriptions")

if __name__ == "__main__":
    main() 