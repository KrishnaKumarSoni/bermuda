/*
  # Fix RLS policies for survey chat sessions

  1. Policy Updates
    - Update INSERT policy for survey_chat_sessions to properly handle anonymous users
    - Update SELECT policy for survey_chat_sessions to allow anonymous users to view their own sessions
    - Ensure policies work correctly with the `auth.uid()` function for anonymous users

  2. Security
    - Maintain security by only allowing access to active surveys
    - Allow anonymous users to create and view sessions for active surveys
    - Ensure survey owners can still view all sessions for their surveys
*/

-- Drop existing policies for survey_chat_sessions
DROP POLICY IF EXISTS "Anyone can create sessions for active surveys" ON survey_chat_sessions;
DROP POLICY IF EXISTS "Anyone can update their own sessions" ON survey_chat_sessions;
DROP POLICY IF EXISTS "Survey owners can view all sessions" ON survey_chat_sessions;

-- Create updated policies for survey_chat_sessions
CREATE POLICY "Anyone can create sessions for active surveys"
  ON survey_chat_sessions
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.is_active = true
    )
  );

CREATE POLICY "Anyone can view sessions for active surveys"
  ON survey_chat_sessions
  FOR SELECT
  TO anon, authenticated
  USING (
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.is_active = true
    )
  );

CREATE POLICY "Anyone can update sessions for active surveys"
  ON survey_chat_sessions
  FOR UPDATE
  TO anon, authenticated
  USING (
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.is_active = true
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.is_active = true
    )
  );

CREATE POLICY "Survey owners can view all sessions"
  ON survey_chat_sessions
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.created_by = auth.uid()
    )
  );

-- Also update policies for survey_chat_messages to ensure consistency
DROP POLICY IF EXISTS "Anyone can create messages for active surveys" ON survey_chat_messages;
DROP POLICY IF EXISTS "Anyone can view messages for active surveys" ON survey_chat_messages;
DROP POLICY IF EXISTS "Survey owners can view all messages" ON survey_chat_messages;

CREATE POLICY "Anyone can create messages for active surveys"
  ON survey_chat_messages
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM survey_chat_sessions scs
      JOIN surveys s ON s.id = scs.survey_id
      WHERE scs.id = survey_chat_messages.session_id 
      AND s.is_active = true
    )
  );

CREATE POLICY "Anyone can view messages for active surveys"
  ON survey_chat_messages
  FOR SELECT
  TO anon, authenticated
  USING (
    EXISTS (
      SELECT 1 FROM survey_chat_sessions scs
      JOIN surveys s ON s.id = scs.survey_id
      WHERE scs.id = survey_chat_messages.session_id 
      AND s.is_active = true
    )
  );

CREATE POLICY "Survey owners can view all messages"
  ON survey_chat_messages
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM survey_chat_sessions scs
      JOIN surveys s ON s.id = scs.survey_id
      WHERE scs.id = survey_chat_messages.session_id 
      AND s.created_by = auth.uid()
    )
  );

-- Update policies for survey_question_responses to ensure consistency
DROP POLICY IF EXISTS "Anyone can manage responses for active surveys" ON survey_question_responses;
DROP POLICY IF EXISTS "Survey owners can view all responses" ON survey_question_responses;

CREATE POLICY "Anyone can manage responses for active surveys"
  ON survey_question_responses
  FOR ALL
  TO anon, authenticated
  USING (
    EXISTS (
      SELECT 1 FROM survey_chat_sessions scs
      JOIN surveys s ON s.id = scs.survey_id
      WHERE scs.id = survey_question_responses.session_id 
      AND s.is_active = true
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM survey_chat_sessions scs
      JOIN surveys s ON s.id = scs.survey_id
      WHERE scs.id = survey_question_responses.session_id 
      AND s.is_active = true
    )
  );

CREATE POLICY "Survey owners can view all responses"
  ON survey_question_responses
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM survey_chat_sessions scs
      JOIN surveys s ON s.id = scs.survey_id
      WHERE scs.id = survey_question_responses.session_id 
      AND s.created_by = auth.uid()
    )
  );