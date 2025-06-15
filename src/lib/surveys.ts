import { supabase } from './supabase'
import { SurveyQuestion } from './openai'

export interface Survey {
  id: string
  title: string
  description?: string
  context: string
  is_active: boolean
  created_by: string
  created_at: string
  updated_at: string
  questions?: SurveyQuestion[]
  demographics?: Array<{ demographic_type: string; is_enabled: boolean }>
  profile_info?: Array<{ profile_type: string; is_enabled: boolean }>
  response_count?: number
}

export interface CreateSurveyData {
  title: string
  context: string
  questions: SurveyQuestion[]
  demographics: Array<{ id: string; enabled: boolean }>
  profileInfo: Array<{ id: string; enabled: boolean }>
}

export async function createSurvey(data: CreateSurveyData): Promise<Survey> {
  const user = await supabase.auth.getUser()
  if (!user.data.user) {
    throw new Error('User not authenticated')
  }

  // Create the survey
  const { data: survey, error: surveyError } = await supabase
    .from('surveys')
    .insert({
      title: data.title,
      context: data.context,
      created_by: user.data.user.id,
    })
    .select()
    .single()

  if (surveyError) {
    throw new Error(`Failed to create survey: ${surveyError.message}`)
  }

  // Create questions
  const questionsToInsert = data.questions.map((question, index) => ({
    survey_id: survey.id,
    question_text: question.question,
    question_type: question.type,
    question_order: index + 1,
    options: question.type === 'mcq' ? question.options : null,
    rating_start: question.type === 'rating' ? question.ratingStart : null,
    rating_end: question.type === 'rating' ? question.ratingEnd : null,
  }))

  const { error: questionsError } = await supabase
    .from('survey_questions')
    .insert(questionsToInsert)

  if (questionsError) {
    throw new Error(`Failed to create questions: ${questionsError.message}`)
  }

  // Create demographics
  const enabledDemographics = data.demographics.filter(d => d.enabled)
  if (enabledDemographics.length > 0) {
    const demographicsToInsert = enabledDemographics.map(demo => ({
      survey_id: survey.id,
      demographic_type: demo.id,
      is_enabled: true,
    }))

    const { error: demographicsError } = await supabase
      .from('survey_demographics')
      .insert(demographicsToInsert)

    if (demographicsError) {
      throw new Error(`Failed to create demographics: ${demographicsError.message}`)
    }
  }

  // Create profile info
  const enabledProfileInfo = data.profileInfo.filter(p => p.enabled)
  if (enabledProfileInfo.length > 0) {
    const profileInfoToInsert = enabledProfileInfo.map(profile => ({
      survey_id: survey.id,
      profile_type: profile.id,
      is_enabled: true,
    }))

    const { error: profileError } = await supabase
      .from('survey_profile_info')
      .insert(profileInfoToInsert)

    if (profileError) {
      throw new Error(`Failed to create profile info: ${profileError.message}`)
    }
  }

  return survey
}

export async function updateSurvey(surveyId: string, data: CreateSurveyData): Promise<Survey> {
  const user = await supabase.auth.getUser()
  if (!user.data.user) {
    throw new Error('User not authenticated')
  }

  // Update the survey
  const { data: survey, error: surveyError } = await supabase
    .from('surveys')
    .update({
      title: data.title,
      context: data.context,
      updated_at: new Date().toISOString()
    })
    .eq('id', surveyId)
    .eq('created_by', user.data.user.id)
    .select()
    .single()

  if (surveyError) {
    throw new Error(`Failed to update survey: ${surveyError.message}`)
  }

  // Delete existing questions
  const { error: deleteQuestionsError } = await supabase
    .from('survey_questions')
    .delete()
    .eq('survey_id', surveyId)

  if (deleteQuestionsError) {
    throw new Error(`Failed to delete existing questions: ${deleteQuestionsError.message}`)
  }

  // Create new questions
  const questionsToInsert = data.questions.map((question, index) => ({
    survey_id: surveyId,
    question_text: question.question,
    question_type: question.type,
    question_order: index + 1,
    options: question.type === 'mcq' ? question.options : null,
    rating_start: question.type === 'rating' ? question.ratingStart : null,
    rating_end: question.type === 'rating' ? question.ratingEnd : null,
  }))

  const { error: questionsError } = await supabase
    .from('survey_questions')
    .insert(questionsToInsert)

  if (questionsError) {
    throw new Error(`Failed to create questions: ${questionsError.message}`)
  }

  // Delete existing demographics
  const { error: deleteDemographicsError } = await supabase
    .from('survey_demographics')
    .delete()
    .eq('survey_id', surveyId)

  if (deleteDemographicsError) {
    throw new Error(`Failed to delete existing demographics: ${deleteDemographicsError.message}`)
  }

  // Create new demographics
  const enabledDemographics = data.demographics.filter(d => d.enabled)
  if (enabledDemographics.length > 0) {
    const demographicsToInsert = enabledDemographics.map(demo => ({
      survey_id: surveyId,
      demographic_type: demo.id,
      is_enabled: true,
    }))

    const { error: demographicsError } = await supabase
      .from('survey_demographics')
      .insert(demographicsToInsert)

    if (demographicsError) {
      throw new Error(`Failed to create demographics: ${demographicsError.message}`)
    }
  }

  // Delete existing profile info
  const { error: deleteProfileError } = await supabase
    .from('survey_profile_info')
    .delete()
    .eq('survey_id', surveyId)

  if (deleteProfileError) {
    throw new Error(`Failed to delete existing profile info: ${deleteProfileError.message}`)
  }

  // Create new profile info
  const enabledProfileInfo = data.profileInfo.filter(p => p.enabled)
  if (enabledProfileInfo.length > 0) {
    const profileInfoToInsert = enabledProfileInfo.map(profile => ({
      survey_id: surveyId,
      profile_type: profile.id,
      is_enabled: true,
    }))

    const { error: profileError } = await supabase
      .from('survey_profile_info')
      .insert(profileInfoToInsert)

    if (profileError) {
      throw new Error(`Failed to create profile info: ${profileError.message}`)
    }
  }

  return survey
}

export async function getUserSurveys(): Promise<Survey[]> {
  const user = await supabase.auth.getUser()
  if (!user.data.user) {
    throw new Error('User not authenticated')
  }

  const { data: surveys, error } = await supabase
    .from('surveys')
    .select(`
      *,
      survey_questions(count)
    `)
    .eq('created_by', user.data.user.id)
    .order('created_at', { ascending: false })

  if (error) {
    throw new Error(`Failed to fetch surveys: ${error.message}`)
  }

  // Get response counts for each survey
  const surveyIds = surveys.map(s => s.id)
  const { data: responseCounts } = await supabase
    .from('survey_responses')
    .select('survey_id')
    .in('survey_id', surveyIds)

  // Count responses per survey
  const responseCountMap = (responseCounts || []).reduce((acc, response) => {
    acc[response.survey_id] = (acc[response.survey_id] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return surveys.map(survey => ({
    ...survey,
    question_count: survey.survey_questions?.[0]?.count || 0,
    response_count: responseCountMap[survey.id] || 0,
  }))
}

export async function getSurveyById(id: string): Promise<Survey | null> {
  const user = await supabase.auth.getUser()
  if (!user.data.user) {
    throw new Error('User not authenticated')
  }

  const { data: survey, error } = await supabase
    .from('surveys')
    .select(`
      *,
      survey_questions(*),
      survey_demographics(*),
      survey_profile_info(*)
    `)
    .eq('id', id)
    .eq('created_by', user.data.user.id)
    .single()

  if (error) {
    if (error.code === 'PGRST116') {
      return null
    }
    throw new Error(`Failed to fetch survey: ${error.message}`)
  }

  // Transform questions back to SurveyQuestion format
  const questions: SurveyQuestion[] = survey.survey_questions
    .sort((a: any, b: any) => a.question_order - b.question_order)
    .map((q: any) => ({
      id: q.id,
      type: q.question_type,
      question: q.question_text,
      ...(q.options && { options: q.options }),
      ...(q.rating_start && { ratingStart: q.rating_start }),
      ...(q.rating_end && { ratingEnd: q.rating_end }),
    }))

  return {
    ...survey,
    questions,
    demographics: survey.survey_demographics,
    profile_info: survey.survey_profile_info,
  }
}

export async function updateSurveyStatus(id: string, isActive: boolean): Promise<void> {
  const user = await supabase.auth.getUser()
  if (!user.data.user) {
    throw new Error('User not authenticated')
  }

  const { error } = await supabase
    .from('surveys')
    .update({ is_active: isActive })
    .eq('id', id)
    .eq('created_by', user.data.user.id)

  if (error) {
    throw new Error(`Failed to update survey status: ${error.message}`)
  }
}

export async function deleteSurvey(id: string): Promise<void> {
  const user = await supabase.auth.getUser()
  if (!user.data.user) {
    throw new Error('User not authenticated')
  }

  const { error } = await supabase
    .from('surveys')
    .delete()
    .eq('id', id)
    .eq('created_by', user.data.user.id)

  if (error) {
    throw new Error(`Failed to delete survey: ${error.message}`)
  }
}