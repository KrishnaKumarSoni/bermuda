/*
  # Survey Chat and Response Tables

  1. New Tables
    - `survey_chat_sessions`
      - `id` (uuid, primary key)
      - `survey_id` (uuid, foreign key to surveys)
      - `respondent_fingerprint` (text, browser fingerprint)
      - `assistant_id` (text, OpenAI assistant ID)
      - `thread_id` (text, OpenAI thread ID)
      - `is_test` (boolean, marks test responses)
      - `status` (text, session status)
      - `started_at` (timestamp)
      - `completed_at` (timestamp)
    
    - `survey_chat_messages`
      - `id` (uuid, primary key)
      - `session_id` (uuid, foreign key to survey_chat_sessions)
      - `role` (text, 'user' or 'assistant')
      - `content` (text, message content)
      - `created_at` (timestamp)
    
    - `survey_question_responses`
      - `id` (uuid, primary key)
      - `session_id` (uuid, foreign key to survey_chat_sessions)
      - `question_id` (uuid, foreign key to survey_questions)
      - `response_text` (text, user's response)
      - `classified_answer` (jsonb, processed answer)
      - `is_valid` (boolean, validation status)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Security
    - Enable RLS on all tables
    - Add policies for survey owners and public access for active surveys
    - Add indexes for performance
*/

-- Survey Chat Sessions Table
CREATE TABLE IF NOT EXISTS survey_chat_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  survey_id uuid REFERENCES surveys(id) ON DELETE CASCADE,
  respondent_fingerprint text NOT NULL,
  assistant_id text,
  thread_id text,
  is_test boolean DEFAULT false,
  status text DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
  started_at timestamptz DEFAULT now(),
  completed_at timestamptz,
  UNIQUE(survey_id, respondent_fingerprint)
);

-- Survey Chat Messages Table
CREATE TABLE IF NOT EXISTS survey_chat_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES survey_chat_sessions(id) ON DELETE CASCADE,
  role text NOT NULL CHECK (role IN ('user', 'assistant')),
  content text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Survey Question Responses Table
CREATE TABLE IF NOT EXISTS survey_question_responses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES survey_chat_sessions(id) ON DELETE CASCADE,
  question_id uuid REFERENCES survey_questions(id) ON DELETE CASCADE,
  response_text text NOT NULL,
  classified_answer jsonb DEFAULT '{}',
  is_valid boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(session_id, question_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_survey_chat_sessions_survey_id ON survey_chat_sessions(survey_id);
CREATE INDEX IF NOT EXISTS idx_survey_chat_sessions_fingerprint ON survey_chat_sessions(respondent_fingerprint);
CREATE INDEX IF NOT EXISTS idx_survey_chat_messages_session_id ON survey_chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_survey_question_responses_session_id ON survey_question_responses(session_id);
CREATE INDEX IF NOT EXISTS idx_survey_question_responses_question_id ON survey_question_responses(question_id);

-- Enable RLS
ALTER TABLE survey_chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_question_responses ENABLE ROW LEVEL SECURITY;

-- RLS Policies for survey_chat_sessions
CREATE POLICY "Survey owners can view all sessions"
  ON survey_chat_sessions
  FOR SELECT
  TO authenticated
  USING (EXISTS (
    SELECT 1 FROM surveys 
    WHERE surveys.id = survey_chat_sessions.survey_id 
    AND surveys.created_by = auth.uid()
  ));

CREATE POLICY "Anyone can create sessions for active surveys"
  ON survey_chat_sessions
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (EXISTS (
    SELECT 1 FROM surveys 
    WHERE surveys.id = survey_chat_sessions.survey_id 
    AND surveys.is_active = true
  ));

CREATE POLICY "Anyone can update their own sessions"
  ON survey_chat_sessions
  FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- RLS Policies for survey_chat_messages
CREATE POLICY "Survey owners can view all messages"
  ON survey_chat_messages
  FOR SELECT
  TO authenticated
  USING (EXISTS (
    SELECT 1 FROM survey_chat_sessions scs
    JOIN surveys s ON s.id = scs.survey_id
    WHERE scs.id = survey_chat_messages.session_id
    AND s.created_by = auth.uid()
  ));

CREATE POLICY "Anyone can view messages for active surveys"
  ON survey_chat_messages
  FOR SELECT
  TO anon, authenticated
  USING (EXISTS (
    SELECT 1 FROM survey_chat_sessions scs
    JOIN surveys s ON s.id = scs.survey_id
    WHERE scs.id = survey_chat_messages.session_id
    AND s.is_active = true
  ));

CREATE POLICY "Anyone can create messages for active surveys"
  ON survey_chat_messages
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (EXISTS (
    SELECT 1 FROM survey_chat_sessions scs
    JOIN surveys s ON s.id = scs.survey_id
    WHERE scs.id = survey_chat_messages.session_id
    AND s.is_active = true
  ));

-- RLS Policies for survey_question_responses
CREATE POLICY "Survey owners can view all responses"
  ON survey_question_responses
  FOR SELECT
  TO authenticated
  USING (EXISTS (
    SELECT 1 FROM survey_chat_sessions scs
    JOIN surveys s ON s.id = scs.survey_id
    WHERE scs.id = survey_question_responses.session_id
    AND s.created_by = auth.uid()
  ));

CREATE POLICY "Anyone can manage responses for active surveys"
  ON survey_question_responses
  FOR ALL
  TO anon, authenticated
  USING (EXISTS (
    SELECT 1 FROM survey_chat_sessions scs
    JOIN surveys s ON s.id = scs.survey_id
    WHERE scs.id = survey_question_responses.session_id
    AND s.is_active = true
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM survey_chat_sessions scs
    JOIN surveys s ON s.id = scs.survey_id
    WHERE scs.id = survey_question_responses.session_id
    AND s.is_active = true
  ));

-- Trigger for updating updated_at
CREATE TRIGGER update_survey_question_responses_updated_at
  BEFORE UPDATE ON survey_question_responses
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();