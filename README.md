# CastLang - Podcast Management System

A full-stack application for downloading, managing, and streaming podcasts from YouTube URLs. Built with FastAPI (backend) and Astro (frontend).

## Features

- **YouTube to MP3 Download**: Convert YouTube videos to high-quality MP3 audio files
- **Podcast Library Management**: Organize and manage your downloaded podcasts
- **Audio Transcription**: Automatic transcription of audio files using Gladia API
- **Streaming Audio Player**: Built-in audio player with seeking and volume controls
- **File Status Monitoring**: Automatic detection of missing files and status updates
- **Re-download Capability**: Re-download podcasts when files are missing or corrupted
- **Series Organization**: Group podcasts by series and episode numbers
- **Metadata Extraction**: Automatic extraction of title, duration, and file size
- **Database Persistence**: PostgreSQL database for reliable data storage
- **Docker Support**: Easy deployment with Docker and docker-compose

## Architecture

- **Backend**: FastAPI with SQLAlchemy ORM and PostgreSQL
- **Frontend**: Astro with TypeScript and Tailwind CSS
- **Database**: PostgreSQL with Alembic migrations
- **Audio Processing**: yt-dlp for YouTube downloads
- **Transcription**: Gladia API for audio-to-text conversion
- **Containerization**: Docker and docker-compose

## Quick Start

### Prerequisites

- Docker and docker-compose
- Python 3.8+ (for local development)
- Node.js 16+ (for frontend development)

### Using Docker (Recommended)

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd castlang
   ```

2. **Create environment file**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**:

   ```bash
   make up
   ```

4. **Access the application**:
   - Frontend: http://localhost:4321
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

1. **Backend Setup**:

   ```bash
   cd backend/app
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**:

   ```bash
   # Start PostgreSQL (using Docker)
   docker run -d --name postgres-castlang \
     -e POSTGRES_DB=castlang \
     -e POSTGRES_USER=castlang \
     -e POSTGRES_PASSWORD=castlang \
     -p 5432:5432 \
     postgres:15
   ```

3. **Frontend Setup**:

   ```bash
   cd frontend/app
   npm install
   ```

4. **Run the application**:

   ```bash
   # Terminal 1 - Backend
   cd backend/app
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

   # Terminal 2 - Frontend
   cd frontend/app
   npm run dev
   ```

## Environment Variables

### Backend (.env)

```env
# Database Configuration
DATABASE_URL=postgresql://castlang:castlang@localhost:5432/castlang
POSTGRES_DB=castlang
POSTGRES_USER=castlang
POSTGRES_PASSWORD=castlang
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
LOG_LEVEL=INFO

# File Storage
DOWNLOADS_DIR=downloads
MAX_FILE_SIZE=1073741824  # 1GB in bytes

# yt-dlp Configuration
AUDIO_FORMAT=bestaudio/best
AUDIO_CODEC=mp3
AUDIO_QUALITY=192

# Transcription Configuration
GLADIA_API_KEY=your_gladia_api_key_here
```

### Frontend (.env)

```env
PUBLIC_API_URL=http://localhost:8000/api/v1
PUBLIC_DEV_MODE=true
PUBLIC_DEBUG=false
PUBLIC_ENABLE_DELETE=true
PUBLIC_ENABLE_DOWNLOAD=true
PUBLIC_ENABLE_STREAMING=true
```

## API Endpoints

### Core Endpoints

- `POST /api/v1/extract-audio` - Download audio from YouTube URL
- `GET /api/v1/audio-files` - List all audio files
- `GET /api/v1/audio-files/{id}` - Get specific audio file details
- `DELETE /api/v1/audio-files/{id}` - Delete audio file
- `GET /api/v1/stream/{filename}` - Stream audio file
- `GET /api/v1/download/{filename}` - Download audio file

### Status Management

- `POST /api/v1/audio-files/check-all-status` - Check status of all audio files
- `POST /api/v1/audio-files/{id}/check-status` - Check status of specific audio file
- `POST /api/v1/audio-files/{id}/re-download` - Re-download audio file
- `PUT /api/v1/audio-files/{id}/status` - Update audio file status

### Series Management

- `GET /api/v1/audio-files/series/{series_name}` - Get audio files by series

### Transcription Endpoints

- `POST /api/v1/audio-files/{id}/transcribe` - Start transcription for an audio file
- `GET /api/v1/audio-files/{id}/transcription-status` - Get transcription status
- `GET /api/v1/audio-files/{id}/transcriptions` - Get all transcriptions for an audio file
- `GET /api/v1/audio-files/{id}/transcriptions/{language}` - Get transcriptions by language
- `GET /api/v1/audio-files/{id}/with-transcriptions` - Get audio file with transcriptions
- `DELETE /api/v1/audio-files/{id}/transcriptions` - Delete all transcriptions for an audio file

### Health Check

- `GET /api/v1/health` - Application health status

## File Status System

The application includes a comprehensive file status monitoring system:

### Status Types

- **`downloaded`**: File is available and ready for streaming/download
- **`downloading`**: File is currently being downloaded
- **`transcribing`**: File is currently being transcribed
- **`transcribed`**: File has been transcribed successfully
- **`transcription_failed`**: Transcription failed
- **`file_missing`**: File was previously downloaded but is no longer present on disk
- **`download_failed`**: Previous download attempt failed
- **`not_downloaded`**: File has not been downloaded yet

### Automatic Status Checking

- Status is automatically checked when listing audio files
- Individual file status is verified when accessing file details
- Manual refresh button available in the UI
- Status updates are reflected in real-time

### Re-download Functionality

- Re-download button appears for files with missing or failed status
- Uses original YouTube URL stored in database
- Updates file metadata after successful re-download
- Maintains file organization and series information

## Audio Transcription

CastLang includes a powerful audio transcription system that automatically converts audio files to text using the Gladia API. This feature is particularly useful for creating searchable transcripts, generating subtitles, or analyzing podcast content.

### Setup

1. **Get a Gladia API Key**:
   - Sign up at [Gladia.io](https://www.gladia.io/)
   - Obtain your free API key
   - Add it to your `.env` file: `GLADIA_API_KEY=your_key_here`

2. **Installation**:
   - The transcription service uses the `requests` package (already included in requirements.txt)
   - No additional setup required

### How Transcription Works

The transcription process follows a sophisticated workflow:

1. **File Validation**: Ensures the audio file exists and is in a supported format
2. **Upload to Gladia**: Uploads the audio file to Gladia's servers using their upload API
3. **Transcription Request**: Sends a transcription request with the uploaded file URL
4. **Polling for Results**: Continuously polls for completion status
5. **Data Storage**: Saves transcription segments to the database with metadata

### Transcription Features

- **Automatic Language Detection**: Detects the primary language of the audio content
- **Speaker Diarization**: Identifies different speakers (configured for 1-3 speakers)
- **Code Switching Support**: Handles mixed-language content seamlessly
- **Confidence Scores**: Provides accuracy scores for each transcription segment
- **Time Stamps**: Includes precise start and end times for each segment
- **Segment Ordering**: Maintains proper chronological order of content
- **Multi-language Support**: Works with any language supported by Gladia

### Usage Examples

#### Start Transcription

```bash
# Start transcription for audio file ID 1
curl -X POST "http://localhost:8000/api/v1/audio-files/1/transcribe"
```

**Response:**
```json
{
  "status": "success",
  "message": "Transcription started successfully",
  "audio_file_id": 1,
  "transcriptions_count": 15
}
```

#### Check Transcription Status

```bash
# Check status of transcription for audio file ID 1
curl "http://localhost:8000/api/v1/audio-files/1/transcription-status"
```

**Response:**
```json
{
  "audio_file_id": 1,
  "status": "transcribed",
  "transcriptions_count": 15
}
```

#### Get All Transcriptions

```bash
# Get all transcription segments for audio file ID 1
curl "http://localhost:8000/api/v1/audio-files/1/transcriptions"
```

**Response:**
```json
[
  {
    "id": 1,
    "audio_file_id": 1,
    "language": "en",
    "content_type": "transcription",
    "content": "Hello everyone, welcome to today's podcast episode.",
    "confidence_score": 0.95,
    "start_time_seconds": 0.0,
    "end_time_seconds": 3.2,
    "segment_order": 1,
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
]
```

#### Get Transcriptions by Language

```bash
# Get transcriptions for a specific language
curl "http://localhost:8000/api/v1/audio-files/1/transcriptions/en"
```

#### Get Audio File with Transcriptions

```bash
# Get complete audio file data including all transcriptions
curl "http://localhost:8000/api/v1/audio-files/1/with-transcriptions"
```

### Transcription Data Structure

Each transcription segment includes:

- **`id`**: Unique identifier for the transcription segment
- **`audio_file_id`**: Reference to the parent audio file
- **`language`**: Language code (e.g., "en", "ja", "fr")
- **`content_type`**: Type of content ("transcription" or "translation")
- **`content`**: The transcribed text content
- **`confidence_score`**: Accuracy score from 0.00 to 1.00
- **`start_time_seconds`**: Start time of the segment in seconds
- **`end_time_seconds`**: End time of the segment in seconds
- **`segment_order`**: Sequential order within the audio file
- **`created_at`**: Timestamp when the transcription was created
- **`updated_at`**: Timestamp when the transcription was last updated

### Error Handling

The transcription service includes robust error handling:

- **File Validation**: Ensures audio files exist before transcription
- **Upload Failures**: Handles network issues during file upload
- **Transcription Failures**: Manages API errors and timeouts
- **Status Updates**: Automatically updates file status on failures
- **Logging**: Comprehensive logging for debugging and monitoring
- **Timeout Protection**: Prevents infinite polling with 5-minute timeout

### Performance Considerations

- **Synchronous Operation**: Transcription is a blocking operation that may take several minutes
- **File Size**: Larger files require more processing time
- **API Limits**: Respects Gladia API rate limits and quotas
- **Database Storage**: Transcription data is stored efficiently with proper indexing
- **Memory Usage**: Optimized for handling large audio files

### Database Schema

The transcription data is stored in the `transcriptions` table:

```sql
CREATE TABLE transcriptions (
    id SERIAL PRIMARY KEY,
    audio_file_id INTEGER REFERENCES audio_files(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    content_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    confidence_score DECIMAL(3, 2),
    start_time_seconds DECIMAL(10, 3),
    end_time_seconds DECIMAL(10, 3),
    segment_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Database Schema

### AudioFile Table

```sql
CREATE TABLE audio_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_url TEXT NOT NULL,
    title VARCHAR(500),
    episode_number INTEGER,
    series_name VARCHAR(255),
    duration_seconds INTEGER,
    file_size_bytes BIGINT,
    file_path TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'not_downloaded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transcriptions Table

```sql
CREATE TABLE transcriptions (
    id SERIAL PRIMARY KEY,
    audio_file_id INTEGER REFERENCES audio_files(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    content_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    confidence_score DECIMAL(3, 2),
    start_time_seconds DECIMAL(10, 3),
    end_time_seconds DECIMAL(10, 3),
    segment_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Development

### Backend Development

```bash
cd backend/app

# Run tests
python test_status_check.py

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Code formatting
black src/
isort src/
```

### Frontend Development

```bash
cd frontend/app

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker Commands

```bash
# Start all services
make up

# Stop all services
make down

# View logs
make logs

# Rebuild containers
make rebuild

# Clean up
make clean
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:

   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Verify network connectivity

2. **File Download Failures**:

   - Check internet connection
   - Verify YouTube URL is accessible
   - Ensure sufficient disk space

3. **Missing Audio Files**:

   - Use the refresh button to check file status
   - Re-download files that show as missing
   - Check file permissions in downloads directory

4. **Frontend Not Loading**:
   - Verify backend API is running
   - Check `PUBLIC_API_URL` in frontend `.env`
   - Clear browser cache

5. **Transcription Failures**:
   - Verify `GLADIA_API_KEY` is set in backend `.env`
   - Check that audio files are downloaded before transcription
   - Ensure sufficient API quota with Gladia
   - Check network connectivity for API calls
   - Review backend logs for detailed error messages

### Logs

```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Database logs
docker-compose logs postgres
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
