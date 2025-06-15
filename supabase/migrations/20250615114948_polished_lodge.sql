/*
  # Update Survey Chat System for Authenticated Respondents

  1. Schema Changes
    - Update survey_chat_sessions to use user_id instead of fingerprint
    - Add respondent_email field for tracking
    - Update foreign key relationships

  2. Security
    - Update RLS policies for authenticated users
    - Ensure proper access control

  3. Tables Modified
    - survey_chat_sessions: Add user_id, respondent_email columns
    - Update all related policies
*/

-- Add new columns to survey_chat_sessions
ALTER TABLE survey_chat_sessions 
ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS respondent_email text;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_survey_chat_sessions_user_id ON survey_chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_survey_chat_sessions_email ON survey_chat_sessions(respondent_email);

-- Drop the old unique constraint and create a new one
ALTER TABLE survey_chat_sessions DROP CONSTRAINT IF EXISTS survey_chat_sessions_survey_id_respondent_fingerprint_key;
CREATE UNIQUE INDEX IF NOT EXISTS survey_chat_sessions_survey_id_user_id_key 
ON survey_chat_sessions(survey_id, user_id) 
WHERE user_id IS NOT NULL;

-- Update RLS policies for survey_chat_sessions
DROP POLICY IF EXISTS "Allow session creation for active surveys" ON survey_chat_sessions;
DROP POLICY IF EXISTS "Users can view own sessions for active surveys" ON survey_chat_sessions;
DROP POLICY IF EXISTS "Users can update own sessions for active surveys" ON survey_chat_sessions;
DROP POLICY IF EXISTS "Survey owners can view all sessions" ON survey_chat_sessions;
DROP POLICY IF EXISTS "Survey owners can update sessions" ON survey_chat_sessions;

-- New policies for authenticated respondents
CREATE POLICY "Authenticated users can create sessions for active surveys"
  ON survey_chat_sessions
  FOR INSERT
  TO authenticated
  WITH CHECK (
    auth.uid() = user_id AND
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.is_active = true
    )
  );

CREATE POLICY "Users can view their own sessions"
  ON survey_chat_sessions
  FOR SELECT
  TO authenticated
  USING (
    auth.uid() = user_id OR
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.created_by = auth.uid()
    )
  );

CREATE POLICY "Users can update their own sessions"
  ON survey_chat_sessions
  FOR UPDATE
  TO authenticated
  USING (
    auth.uid() = user_id OR
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.created_by = auth.uid()
    )
  )
  WITH CHECK (
    auth.uid() = user_id OR
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.created_by = auth.uid()
    )
  );

-- Update policies for survey_chat_messages
DROP POLICY IF EXISTS "Anyone can create messages for active surveys" ON survey_chat_messages;
DROP POLICY IF EXISTS "Anyone can view messages for active surveys" ON survey_chat_messages;
DROP POLICY IF EXISTS "Survey owners can view all messages" ON survey_chat_messages;

CREATE POLICY "Authenticated users can create messages for their sessions"
  ON survey_chat_messages
  FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM survey_chat_sessions scs
      JOIN surveys s ON s.id = scs.survey_id
      WHERE scs.id = survey_chat_messages.session_id 
      AND (scs.user_id = auth.uid() OR s.created_by = auth.uid())
      AND s.is_active = true
    )
  );

CREATE POLICY "Users can view messages for their sessions"
  ON survey_chat_messages
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM survey_chat_sessions scs
      JOIN surveys s ON s.id = scs.survey_id
      WHERE scs.id = survey_chat_messages.session_id 
      AND (scs.user_id = auth.uid() OR s.created_by = auth.uid())
    )
  );

-- Update policies for survey_question_responses
DROP POLICY IF EXISTS "Anyone can manage responses for active surveys" ON survey_question_responses;
DROP POLICY IF EXISTS "Survey owners can view all responses" ON survey_question_responses;

CREATE POLICY "Users can manage their own responses"
  ON survey_question_responses
  FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM survey_chat_sessions scs
      JOIN surveys s ON s.id = scs.survey_id
      WHERE scs.id = survey_question_responses.session_id 
      AND (scs.user_id = auth.uid() OR s.created_by = auth.uid())
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM survey_chat_sessions scs
      JOIN surveys s ON s.id = scs.survey_id
      WHERE scs.id = survey_question_responses.session_id 
      AND (scs.user_id = auth.uid() OR s.created_by = auth.uid())
      AND s.is_active = true
    )
  );