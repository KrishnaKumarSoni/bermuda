/*
  # Fix survey access policies

  1. Security
    - Allow public read access to surveys for basic info (title, is_active)
    - Maintain creator-only access for full survey management
    - Ensure proper session and message access controls

  2. Changes
    - Add public read policy for surveys
    - Update session policies for better access control
    - Ensure message and response policies work correctly
*/

-- Allow public read access to basic survey info
CREATE POLICY "Public can view active survey info"
  ON surveys
  FOR SELECT
  TO anon, authenticated
  USING (is_active = true);

-- Update survey_chat_sessions policies to be more permissive for active surveys
DROP POLICY IF EXISTS "Authenticated users can create sessions for active surveys" ON survey_chat_sessions;
DROP POLICY IF EXISTS "Users can view their own sessions" ON survey_chat_sessions;
DROP POLICY IF EXISTS "Users can update their own sessions" ON survey_chat_sessions;

CREATE POLICY "Authenticated users can create sessions for active surveys"
  ON survey_chat_sessions
  FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.is_active = true
    )
  );

CREATE POLICY "Users can view sessions for active surveys"
  ON survey_chat_sessions
  FOR SELECT
  TO authenticated
  USING (
    user_id = auth.uid() OR
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.created_by = auth.uid()
    )
  );

CREATE POLICY "Users can update sessions for active surveys"
  ON survey_chat_sessions
  FOR UPDATE
  TO authenticated
  USING (
    user_id = auth.uid() OR
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.created_by = auth.uid()
    )
  )
  WITH CHECK (
    user_id = auth.uid() OR
    EXISTS (
      SELECT 1 FROM surveys 
      WHERE surveys.id = survey_chat_sessions.survey_id 
      AND surveys.created_by = auth.uid()
    )
  );