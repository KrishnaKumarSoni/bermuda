import OpenAI from 'openai'

const openai = new OpenAI({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true
})

export interface SurveyQuestion {
  id: string
  type: 'mcq' | 'text' | 'yes_no' | 'rating'
  question: string
  options?: string[]
  ratingStart?: number
  ratingEnd?: number
}

export interface GeneratedSurvey {
  title: string
  questions: SurveyQuestion[]
}

export async function generateSurveyQuestions(context: string): Promise<GeneratedSurvey> {
  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: `You are a survey expert. Generate a survey title and questions based on the provided context. Return a JSON object with the following structure:
          {
            "title": "Survey Title",
            "questions": [
              {
                "id": "unique_id",
                "type": "mcq" | "text" | "yes_no" | "rating",
                "question": "question text",
                "options": ["option1", "option2", "option3", "option4"] (only for mcq),
                "ratingStart": 1 (only for rating, must be > 0),
                "ratingEnd": 5 (only for rating, must be > ratingStart)
              }
            ]
          }
          
          Generate a clear, descriptive title that captures the essence of the survey. Generate 15-20 comprehensive and relevant questions. Create a thorough survey that covers all important aspects of the topic. Mix different question types appropriately - use multiple choice, text responses, yes/no questions, and rating scales. Make sure questions are diverse, well-structured, and provide comprehensive coverage of the subject matter.`
        },
        {
          role: 'user',
          content: context
        }
      ],
      temperature: 0.7
    })

    const content = response.choices[0]?.message?.content
    if (!content) throw new Error('No response from OpenAI')

    // Clean the content by removing markdown code block fences
    const cleanedContent = content
      .replace(/^```json\s*/, '')
      .replace(/\s*```$/, '')
      .trim()
    
    const result = JSON.parse(cleanedContent)
    
    return {
      title: result.title,
      questions: result.questions.map((q: any, index: number) => ({
        ...q,
        id: q.id || `question_${index + 1}`
      }))
    }
  } catch (error) {
    console.error('Error generating survey questions:', error)
    throw error
  }
}

// Legacy function for backward compatibility
export async function generateSurveyQuestionsOnly(context: string): Promise<SurveyQuestion[]> {
  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: `You are a survey expert. Generate survey questions based on the provided context. Return a JSON array of questions with the following structure:
          {
            "id": "unique_id",
            "type": "mcq" | "text" | "yes_no" | "rating",
            "question": "question text",
            "options": ["option1", "option2", "option3", "option4"] (only for mcq),
            "ratingStart": 1 (only for rating, must be > 0),
            "ratingEnd": 5 (only for rating, must be > ratingStart)
          }
          
          Generate 15-20 comprehensive and relevant questions. Create a thorough survey that covers all important aspects of the topic. Mix different question types appropriately - use multiple choice, text responses, yes/no questions, and rating scales. Make sure questions are diverse, well-structured, and provide comprehensive coverage of the subject matter.`
        },
        {
          role: 'user',
          content: context
        }
      ],
      temperature: 0.7
    })

    const content = response.choices[0]?.message?.content
    if (!content) throw new Error('No response from OpenAI')

    // Clean the content by removing markdown code block fences
    const cleanedContent = content
      .replace(/^```json\s*/, '')
      .replace(/\s*```$/, '')
      .trim()
    
    const questions = JSON.parse(cleanedContent)
    return questions.map((q: any, index: number) => ({
      ...q,
      id: q.id || `question_${index + 1}`
    }))
  } catch (error) {
    console.error('Error generating survey questions:', error)
    throw error
  }
}