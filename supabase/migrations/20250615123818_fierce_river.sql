/*
  # Fix respondent_fingerprint column constraint

  1. Changes
    - Make respondent_fingerprint column nullable since we now use user_id and respondent_email
    - Update the column to allow NULL values
    - This fixes the "null value in column respondent_fingerprint violates not-null constraint" error

  2. Security
    - No changes to RLS policies needed
    - Maintains existing security model
*/

-- Make respondent_fingerprint nullable since we now use user_id and respondent_email
ALTER TABLE survey_chat_sessions 
ALTER COLUMN respondent_fingerprint DROP NOT NULL;

-- Update any existing records that might have issues
UPDATE survey_chat_sessions 
SET respondent_fingerprint = COALESCE(respondent_fingerprint, 'legacy_' || id::text)
WHERE respondent_fingerprint IS NULL;