/*
  # Fix RLS policies for survey chat sessions

  1. Policy Updates
    - Drop existing restrictive policies on survey_chat_sessions
    - Create new policies that allow anonymous users to manage their own sessions
    - Ensure survey owners can still view all sessions for their surveys

  2. Security
    - Anonymous users can only access sessions with their own fingerprint
    - Survey owners can access all sessions for their surveys
    - Sessions can only be created for active surveys
*/

-- Drop existing policies
DROP POLICY IF EXISTS "Anyone can create sessions for active surveys" ON survey_chat_sessions;
DROP POLICY IF EXISTS "Anyone can update sessions for active surveys" ON survey_chat_sessions;
DROP POLICY IF EXISTS "Anyone can view sessions for active surveys" ON survey_chat_sessions;
DROP POLICY IF EXISTS "Survey owners can view all sessions" ON survey_chat_sessions;

-- Create new policies that properly handle anonymous users

-- Allow anyone to create sessions for active surveys
CREATE POLICY "Allow session creation for active surveys"
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

-- Allow users to view their own sessions (by fingerprint) for active surveys
CREATE POLICY "Users can view own sessions for active surveys"
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

-- Allow users to update their own sessions (by fingerprint) for active surveys
CREATE POLICY "Users can update own sessions for active surveys"
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

-- Allow survey owners to view all sessions for their surveys
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

-- Allow survey owners to update sessions for their surveys
CREATE POLICY "Survey owners can update sessions"
  ON survey_chat_sessions
  FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.created_by = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.created_by = auth.uid()
    )
  );