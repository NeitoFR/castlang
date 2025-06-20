-- Manual migration script to add new columns for existing databases
-- Run this if alembic migration hasn't been applied yet

-- Add new columns if they don't exist
DO $$
BEGIN
    -- Add download_status column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'audio_files' AND column_name = 'download_status') THEN
        ALTER TABLE audio_files ADD COLUMN download_status VARCHAR(50) DEFAULT 'not_downloaded';
    END IF;
    
    -- Add transcription_status column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'audio_files' AND column_name = 'transcription_status') THEN
        ALTER TABLE audio_files ADD COLUMN transcription_status VARCHAR(50) DEFAULT 'not_transcribed';
    END IF;
    
    -- Add available_languages column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'audio_files' AND column_name = 'available_languages') THEN
        ALTER TABLE audio_files ADD COLUMN available_languages JSON DEFAULT '[]'::json;
    END IF;
END $$;

-- Migrate existing data from old status field to new fields
UPDATE audio_files 
SET 
    download_status = CASE 
        WHEN status IN ('downloaded', 'downloading', 'download_failed', 'file_missing', 'not_downloaded') 
        THEN status 
        ELSE 'downloaded'
    END,
    transcription_status = CASE 
        WHEN status IN ('transcribed', 'transcribing', 'transcription_failed') 
        THEN status 
        ELSE 'not_transcribed'
    END,
    available_languages = '[]'::json
WHERE download_status IS NULL OR transcription_status IS NULL OR available_languages IS NULL;

-- Make sure all records have proper values
UPDATE audio_files SET download_status = 'not_downloaded' WHERE download_status IS NULL;
UPDATE audio_files SET transcription_status = 'not_transcribed' WHERE transcription_status IS NULL;
UPDATE audio_files SET available_languages = '[]'::json WHERE available_languages IS NULL; 