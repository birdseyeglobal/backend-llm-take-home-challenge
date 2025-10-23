-- Migration script to add background task support to content_analysis table
-- Run this against your Neon database

-- Add status column
ALTER TABLE content_analysis 
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending';

-- Add error_message column
ALTER TABLE content_analysis 
ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Make warmth_score nullable (allow NULL during pending state)
ALTER TABLE content_analysis 
ALTER COLUMN warmth_score DROP NOT NULL;

-- Make target_demographic nullable (allow NULL during pending state)
ALTER TABLE content_analysis 
ALTER COLUMN target_demographic DROP NOT NULL;

-- Update existing records to have status='completed'
UPDATE content_analysis 
SET status = 'completed' 
WHERE status IS NULL OR status = '';

-- Verify the changes
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'content_analysis'
ORDER BY ordinal_position;

