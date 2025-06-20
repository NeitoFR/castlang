# Database Schema Design

This document outlines the database schema for the Japanese Podcast Player application, designed to store audio file metadata and transcription/translation data.

## Overview

The database consists of two main entities:

1. **Audio Files** - Metadata about downloaded audio files
2. **Transcriptions** - Text content and translations of audio files

## Schema Design

### 1. Audio Files Table

Stores information about downloaded audio files including metadata and file details.

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
    file_path VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'not_downloaded', -- downloaded, not_downloaded
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX idx_audio_files_episode ON audio_files(episode_number);
CREATE INDEX idx_audio_files_series ON audio_files(series_name);
```

### 2. Transcriptions Table

Stores transcription and translation data for audio files.

```sql
CREATE TABLE transcriptions (
    id SERIAL PRIMARY KEY,
    audio_file_id INTEGER REFERENCES audio_files(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL, -- 'ja', 'en', 'fr'
    content_type VARCHAR(20) NOT NULL, -- 'transcription', 'translation'
    content TEXT NOT NULL,
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    start_time_seconds DECIMAL(10,3),
    end_time_seconds DECIMAL(10,3),
    segment_order INTEGER, -- For ordering segments within a file
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_transcriptions_audio_file ON transcriptions(audio_file_id);
CREATE INDEX idx_transcriptions_language ON transcriptions(language);
CREATE INDEX idx_transcriptions_content_type ON transcriptions(content_type);
CREATE INDEX idx_transcriptions_time_range ON transcriptions(start_time_seconds, end_time_seconds);
```

## Data Relationships

```
audio_files (1) -----> (many) transcriptions
```

- One audio file can have multiple transcription segments
- Each transcription can be in different languages (Japanese, English, French)
- Each transcription can be either original transcription or translation

## Example Data

### Audio Files

```sql
INSERT INTO audio_files (filename, original_url, title, episode_number, series_name, duration_seconds, file_path)
VALUES (
    'japanese_podcast_episode_001.mp3',
    'https://example.com/podcast/episode-001',
    'Japanese Learning Podcast - Episode 1: Basic Greetings',
    1,
    'Japanese Learning Podcast',
    1800,
    '/downloads/japanese_podcast_episode_001.mp3'
);
```

### Transcriptions

```sql
-- Japanese transcription
INSERT INTO transcriptions (audio_file_id, language, content_type, content, start_time_seconds, end_time_seconds, segment_order)
VALUES (
    1, 'ja', 'transcription', '**こんにちは、皆さん。今日は基本的な挨拶について学びましょ**う。',
    0.0, 5.2, 1
);

-- English translation
INSERT INTO transcriptions (audio_file_id, language, content_type, content, start_time_seconds, end_time_seconds, segment_order)
VALUES (
    1, 'en', 'translation', 'Hello everyone. Today we will learn about basic greetings.',
    0.0, 5.2, 1
);

-- French translation
INSERT INTO transcriptions (audio_file_id, language, content_type, content, start_time_seconds, end_time_seconds, segment_order)
VALUES (
    1, 'fr', 'translation', 'Bonjour à tous. Aujourd''hui, nous allons apprendre les salutations de base.',
    0.0, 5.2, 1
);
```

## Query Examples

### Get all episodes of a series

```sql
SELECT * FROM audio_files
WHERE series_name = 'Japanese Learning Podcast'
ORDER BY episode_number;
```

### Get transcription with translations for a specific time range

```sql
SELECT
    af.title,
    t.language,
    t.content_type,
    t.content,
    t.start_time_seconds,
    t.end_time_seconds
FROM audio_files af
JOIN transcriptions t ON af.id = t.audio_file_id
WHERE af.id = 1
    AND t.start_time_seconds >= 10.0
    AND t.end_time_seconds <= 20.0
ORDER BY t.segment_order, t.language;
```

### Get all available languages for an audio file

```sql
SELECT DISTINCT language
FROM transcriptions
WHERE audio_file_id = 1;
```

## Schema Updates

To apply these schemas to your database:

1. Connect to your PostgreSQL database:

   ```bash
   psql -h localhost -U castlang -d castlang
   ```

2. Run the CREATE TABLE statements above

3. Verify the tables were created:
   ```sql
   \dt
   \d audio_files
   \d transcriptions
   ```

## Future Considerations

- **Audio Quality**: Add fields for audio quality, bitrate, format
- **Tags/Categories**: Add tagging system for better organization
- **User Preferences**: Store user-specific settings and preferences
- **Playback History**: Track listening progress and history
- **Notes/Bookmarks**: Allow users to add personal notes to specific timestamps
