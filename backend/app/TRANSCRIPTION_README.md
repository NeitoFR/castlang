# Audio Transcription with Gladia API

This backend now supports audio file transcription using the Gladia API v2. The transcription service follows the correct Gladia workflow: upload the audio file first, then transcribe it using the returned audio URL.

## Setup

### 1. Environment Variables

Add the following environment variable to your `.env` file:

```bash
GLADIA_API_KEY=your_gladia_api_key_here
```

You can get a free API key by signing up at [Gladia.io](https://www.gladia.io/).

### 2. Install Dependencies

The transcription service uses the `requests` package, which is already included in `requirements.txt`.

## How It Works

The transcription process follows the official Gladia API workflow:

1. **Upload Audio File** - Upload the audio file to Gladia's servers using `POST /v2/upload/`
2. **Start Transcription** - Send transcription request using `POST /v2/pre-recorded/` with the returned audio URL
3. **Poll for Results** - Continuously poll the result URL until transcription is complete
4. **Save Results** - Store transcription segments in the database

## API Endpoints

### Start Transcription

**POST** `/audio-files/{audio_file_id}/transcribe`

Start transcription for a downloaded audio file. This is a synchronous operation that may take several minutes.

**Response:**

```json
{
  "status": "success",
  "message": "Transcription started successfully",
  "audio_file_id": 1,
  "transcriptions_count": 15
}
```

### Get Transcription Status

**GET** `/audio-files/{audio_file_id}/transcription-status`

Get the current transcription status for an audio file.

**Response:**

```json
{
  "audio_file_id": 1,
  "status": "transcribed",
  "transcriptions_count": 15
}
```

### Get All Transcriptions

**GET** `/audio-files/{audio_file_id}/transcriptions`

Get all transcription segments for an audio file.

**Response:**

```json
[
  {
    "id": 1,
    "audio_file_id": 1,
    "language": "ja",
    "content_type": "transcription",
    "content": "こんにちは、皆さん。今日は基本的な挨拶について学びましょう。",
    "confidence_score": 0.95,
    "start_time_seconds": 0.0,
    "end_time_seconds": 5.2,
    "segment_order": 1,
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
]
```

### Get Transcriptions by Language

**GET** `/audio-files/{audio_file_id}/transcriptions/{language}`

Get transcription segments for a specific language (e.g., "ja", "en", "fr").

### Get Audio File with Transcriptions

**GET** `/audio-files/{audio_file_id}/with-transcriptions`

Get an audio file with all its transcription data included.

### Delete Transcriptions

**DELETE** `/audio-files/{audio_file_id}/transcriptions`

Delete all transcription data for an audio file.

## Audio File Status Values

The audio file status field now supports additional values for transcription:

- `not_downloaded` - File has not been downloaded yet
- `downloading` - File is currently being downloaded
- `downloaded` - File has been downloaded successfully
- `transcribing` - File is currently being transcribed
- `transcribed` - File has been transcribed successfully
- `transcription_failed` - Transcription failed
- `file_missing` - File was deleted from disk
- `download_failed` - Download failed

## Transcription Features

The transcription service includes the following features:

- **File Upload** - Automatically uploads audio files to Gladia's servers
- **Automatic Language Detection** - Detects the language of the audio content
- **Speaker Diarization** - Identifies different speakers (configured for 1-3 speakers)
- **Code Switching Support** - Handles mixed-language content
- **Confidence Scores** - Provides confidence scores for transcription accuracy
- **Time Stamps** - Includes start and end times for each transcription segment
- **Segment Ordering** - Maintains proper order of transcription segments
- **Polling Mechanism** - Automatically polls for results until completion

## Usage Example

1. **Download an audio file:**

   ```bash
   curl -X POST "http://localhost:8000/extract-audio" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://www.youtube.com/watch?v=example"}'
   ```

2. **Start transcription:**

   ```bash
   curl -X POST "http://localhost:8000/audio-files/1/transcribe"
   ```

   _Note: This will take several minutes to complete_

3. **Check transcription status:**

   ```bash
   curl "http://localhost:8000/audio-files/1/transcription-status"
   ```

4. **Get transcriptions:**
   ```bash
   curl "http://localhost:8000/audio-files/1/transcriptions"
   ```

## Error Handling

The transcription service includes comprehensive error handling:

- Validates that audio files exist and are downloaded before transcription
- Handles upload failures and provides detailed error messages
- Manages transcription request failures
- Implements timeout protection for long-running transcriptions
- Updates file status appropriately on failures
- Logs all operations for debugging

## Technical Details

### Upload Process

- Uses `multipart/form-data` to upload audio files
- Supports various audio formats (MP3, WAV, etc.)
- Returns an `audio_url` for use in transcription

### Transcription Process

- Sends JSON request with audio URL and configuration
- Configures diarization for 1-3 speakers
- Enables language detection and code switching
- Returns a `result_url` for polling

### Polling Process

- Polls the result URL every second
- Continues until status is "done" or "error"
- Times out after 5 minutes (300 attempts)
- Handles various status states

## Database Schema

The transcription data is stored in the `transcriptions` table with the following structure:

- `audio_file_id` - Reference to the audio file
- `language` - Language code (e.g., "ja", "en", "fr")
- `content_type` - Type of content ("transcription" or "translation")
- `content` - The transcribed text
- `confidence_score` - Confidence score (0.00 to 1.00)
- `start_time_seconds` - Start time of the segment
- `end_time_seconds` - End time of the segment
- `segment_order` - Order of the segment within the file

## Notes

- Transcription is a synchronous operation that may take several minutes for longer audio files
- The service automatically handles file upload and polling
- All transcription data is stored in the database for later retrieval
- The service is optimized for Japanese podcast content but works with any language
- The polling mechanism ensures reliable completion of transcription tasks
