# CastLang Backend

This is the backend API for the CastLang Japanese Podcast Player application.

## Environment Configuration

Create a `.env` file in the `backend/app/` directory with the following configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=castlang
DB_USER=castlang
DB_PASSWORD=castlang

# Alternative: Use DATABASE_URL directly
# DATABASE_URL=postgresql://castlang:castlang@localhost:5432/castlang

# Application Configuration
APP_TITLE=CastLang API
APP_VERSION=1.0.0
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true

# CORS Configuration
CORS_ORIGINS=*,http://localhost:4321,http://127.0.0.1:4321

# File Storage Configuration
DOWNLOADS_DIR=downloads

# Audio Download Configuration
AUDIO_FORMAT=bestaudio/best
AUDIO_CODEC=mp3
AUDIO_QUALITY=192

# Database Debugging (optional)
DB_ECHO=false
```

## Database Setup

The application now uses PostgreSQL with SQLAlchemy ORM. Follow these steps to set up the database:

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up PostgreSQL Database

Create the database and user:

```sql
CREATE DATABASE castlang;
CREATE USER castlang WITH PASSWORD 'castlang';
GRANT ALL PRIVILEGES ON DATABASE castlang TO castlang;
```

### 3. Initialize Database

Run the database initialization script:

```bash
python init_db.py
```

### 4. Start the Application

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Audio Files

- `POST /api/v1/extract-audio` - Download audio from YouTube URL
- `GET /api/v1/audio-files` - List all audio files
- `GET /api/v1/audio-files/{id}` - Get specific audio file
- `GET /api/v1/audio-files/series/{series_name}` - Get audio files by series
- `PUT /api/v1/audio-files/{id}/status` - Update audio file status
- `DELETE /api/v1/audio-files/{id}` - Delete audio file
- `GET /api/v1/stream/{filename}` - Stream audio file
- `GET /api/v1/download/{filename}` - Download audio file

### Health Check

- `GET /api/v1/health` - Health check endpoint

## Database Schema

The application uses two main tables:

### audio_files

- `id` - Primary key
- `filename` - Sanitized filename
- `original_url` - Original YouTube URL
- `title` - Video title
- `episode_number` - Episode number (if available)
- `series_name` - Series name (if available)
- `duration_seconds` - Audio duration
- `file_size_bytes` - File size in bytes
- `file_path` - Path to the audio file
- `status` - Download status ('downloaded', 'not_downloaded')
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### transcriptions

- `id` - Primary key
- `audio_file_id` - Foreign key to audio_files
- `language` - Language code ('ja', 'en', 'fr')
- `content_type` - Content type ('transcription', 'translation')
- `content` - Text content
- `confidence_score` - Confidence score (0.00-1.00)
- `start_time_seconds` - Start time in seconds
- `end_time_seconds` - End time in seconds
- `segment_order` - Segment order within file
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## Development

### Running with Docker

```bash
docker-compose up backend
```

### Running Locally

1. Make sure PostgreSQL is running
2. Create the `.env` file as shown above
3. Set up the database as described above
4. Run the application:

```bash
cd backend/app
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation will be available at `http://localhost:8000/docs`

## Environment Variables Reference

| Variable        | Default          | Description                                          |
| --------------- | ---------------- | ---------------------------------------------------- |
| `DB_HOST`       | `localhost`      | Database host                                        |
| `DB_PORT`       | `5432`           | Database port                                        |
| `DB_NAME`       | `castlang`       | Database name                                        |
| `DB_USER`       | `castlang`       | Database username                                    |
| `DB_PASSWORD`   | `castlang`       | Database password                                    |
| `DATABASE_URL`  | -                | Full database URL (overrides individual DB\_\* vars) |
| `APP_TITLE`     | `CastLang API`   | Application title                                    |
| `APP_VERSION`   | `1.0.0`          | Application version                                  |
| `APP_HOST`      | `0.0.0.0`        | Application host                                     |
| `APP_PORT`      | `8000`           | Application port                                     |
| `DEBUG`         | `false`          | Debug mode                                           |
| `CORS_ORIGINS`  | `*`              | CORS allowed origins (comma-separated)               |
| `DOWNLOADS_DIR` | `downloads`      | Directory for downloaded files                       |
| `AUDIO_FORMAT`  | `bestaudio/best` | yt-dlp audio format                                  |
| `AUDIO_CODEC`   | `mp3`            | Audio codec                                          |
| `AUDIO_QUALITY` | `192`            | Audio quality                                        |
| `DB_ECHO`       | `false`          | SQL query logging                                    |
