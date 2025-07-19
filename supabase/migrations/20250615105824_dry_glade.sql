/*
  # Create surveys and related tables

  1. New Tables
    - `surveys`
      - `id` (uuid, primary key)
      - `title` (text)
      - `description` (text)
      - `context` (text)
      - `is_active` (boolean, default false)
      - `created_by` (uuid, references auth.users)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
    
    - `survey_questions`
      - `id` (uuid, primary key)
      - `survey_id` (uuid, references surveys)
      - `question_text` (text)
      - `question_type` (text)
      - `question_order` (integer)
      - `options` (jsonb, for MCQ options)
      - `rating_start` (integer, for rating questions)
      - `rating_end` (integer, for rating questions)
      - `created_at` (timestamp)
    
    - `survey_demographics`
      - `id` (uuid, primary key)
      - `survey_id` (uuid, references surveys)
      - `demographic_type` (text)
      - `is_enabled` (boolean)
    
    - `survey_profile_info`
      - `id` (uuid, primary key)
      - `survey_id` (uuid, references surveys)
      - `profile_type` (text)
      - `is_enabled` (boolean)
    
    - `survey_responses`
      - `id` (uuid, primary key)
      - `survey_id` (uuid, references surveys)
      - `respondent_id` (uuid, optional)
      - `response_data` (jsonb)
      - `demographics_data` (jsonb)
      - `profile_data` (jsonb)
      - `submitted_at` (timestamp)

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated users to manage their own surveys
    - Add policies for public access to active surveys for responses
*/

-- Create surveys table
CREATE TABLE IF NOT EXISTS surveys (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  description text,
  context text NOT NULL,
  is_active boolean DEFAULT false,
  created_by uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create survey_questions table
CREATE TABLE IF NOT EXISTS survey_questions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  survey_id uuid REFERENCES surveys(id) ON DELETE CASCADE,
  question_text text NOT NULL,
  question_type text NOT NULL CHECK (question_type IN ('mcq', 'text', 'yes_no', 'rating')),
  question_order integer NOT NULL,
  options jsonb DEFAULT NULL,
  rating_start integer DEFAULT NULL,
  rating_end integer DEFAULT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create survey_demographics table
CREATE TABLE IF NOT EXISTS survey_demographics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  survey_id uuid REFERENCES surveys(id) ON DELETE CASCADE,
  demographic_type text NOT NULL,
  is_enabled boolean DEFAULT true
);

-- Create survey_profile_info table
CREATE TABLE IF NOT EXISTS survey_profile_info (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  survey_id uuid REFERENCES surveys(id) ON DELETE CASCADE,
  profile_type text NOT NULL,
  is_enabled boolean DEFAULT true
);

-- Create survey_responses table
CREATE TABLE IF NOT EXISTS survey_responses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  survey_id uuid REFERENCES surveys(id) ON DELETE CASCADE,
  respondent_id uuid DEFAULT NULL,
  response_data jsonb NOT NULL DEFAULT '{}',
  demographics_data jsonb DEFAULT '{}',
  profile_data jsonb DEFAULT '{}',
  submitted_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE surveys ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_demographics ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_profile_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_responses ENABLE ROW LEVEL SECURITY;

-- Policies for surveys
CREATE POLICY "Users can view their own surveys"
  ON surveys
  FOR SELECT
  TO authenticated
  USING (auth.uid() = created_by);

CREATE POLICY "Users can create surveys"
  ON surveys
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can update their own surveys"
  ON surveys
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = created_by)
  WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can delete their own surveys"
  ON surveys
  FOR DELETE
  TO authenticated
  USING (auth.uid() = created_by);

-- Policies for survey_questions
CREATE POLICY "Users can view questions for their surveys"
  ON survey_questions
  FOR SELECT
  TO authenticated
  USING (EXISTS (
    SELECT 1 FROM surveys 
    WHERE surveys.id = survey_questions.survey_id 
    AND surveys.created_by = auth.uid()
  ));

CREATE POLICY "Users can create questions for their surveys"
  ON survey_questions
  FOR INSERT
  TO authenticated
  WITH CHECK (EXISTS (
    SELECT 1 FROM surveys 
    WHERE surveys.id = survey_questions.survey_id 
    AND surveys.created_by = auth.uid()
  ));

CREATE POLICY "Users can update questions for their surveys"
  ON survey_questions
  FOR UPDATE
  TO authenticated
  USING (EXISTS (
    SELECT 1 FROM surveys 
    WHERE surveys.id = survey_questions.survey_id 
    AND surveys.created_by = auth.uid()
  ));

CREATE POLICY "Users can delete questions for their surveys"
  ON survey_questions
  FOR DELETE
  TO authenticated
  USING (EXISTS (
    SELECT 1 FROM surveys 
    WHERE surveys.id = survey_questions.survey_id 
    AND surveys.created_by = auth.uid()
  ));

-- Policies for survey_demographics
CREATE POLICY "Users can manage demographics for their surveys"
  ON survey_demographics
  FOR ALL
  TO authenticated
  USING (EXISTS (
    SELECT 1 FROM surveys 
    WHERE surveys.id = survey_demographics.survey_id 
    AND surveys.created_by = auth.uid()
  ));

-- Policies for survey_profile_info
CREATE POLICY "Users can manage profile info for their surveys"
  ON survey_profile_info
  FOR ALL
  TO authenticated
  USING (EXISTS (
    SELECT 1 FROM surveys 
    WHERE surveys.id = survey_profile_info.survey_id 
    AND surveys.created_by = auth.uid()
  ));

-- Policies for survey_responses (public can respond to active surveys)
CREATE POLICY "Anyone can view responses for active surveys"
  ON survey_responses
  FOR SELECT
  TO anon, authenticated
  USING (EXISTS (
    SELECT 1 FROM surveys 
    WHERE surveys.id = survey_responses.survey_id 
    AND surveys.is_active = true
  ));

CREATE POLICY "Anyone can submit responses to active surveys"
  ON survey_responses
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (EXISTS (
    SELECT 1 FROM surveys 
    WHERE surveys.id = survey_responses.survey_id 
    AND surveys.is_active = true
  ));

CREATE POLICY "Survey owners can view all responses"
  ON survey_responses
  FOR SELECT
  TO authenticated
  USING (EXISTS (
    SELECT 1 FROM surveys 
    WHERE surveys.id = survey_responses.survey_id 
    AND surveys.created_by = auth.uid()
  ));

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_surveys_created_by ON surveys(created_by);
CREATE INDEX IF NOT EXISTS idx_survey_questions_survey_id ON survey_questions(survey_id);
CREATE INDEX IF NOT EXISTS idx_survey_questions_order ON survey_questions(survey_id, question_order);
CREATE INDEX IF NOT EXISTS idx_survey_demographics_survey_id ON survey_demographics(survey_id);
CREATE INDEX IF NOT EXISTS idx_survey_profile_info_survey_id ON survey_profile_info(survey_id);
CREATE INDEX IF NOT EXISTS idx_survey_responses_survey_id ON survey_responses(survey_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for surveys table
CREATE TRIGGER update_surveys_updated_at 
    BEFORE UPDATE ON surveys 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();