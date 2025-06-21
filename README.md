# CastLang - Podcast Management System

A full-stack application for downloading, managing, and streaming podcasts from YouTube URLs. Built with FastAPI (backend) and Astro (frontend).

## Features

- **YouTube to MP3 Download**: Convert YouTube videos to high-quality MP3 audio files
- **Podcast Library Management**: Organize and manage your downloaded podcasts
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

### Health Check

- `GET /api/v1/health` - Application health status

## File Status System

The application includes a comprehensive file status monitoring system:

### Status Types

- **`downloaded`**: File is available and ready for streaming/download
- **`downloading`**: File is currently being downloaded
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
