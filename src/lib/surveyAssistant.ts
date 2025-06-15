import OpenAI from 'openai';
import { supabase } from './supabase';

const openai = new OpenAI({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true
});

export interface SurveySession {
  id: string;
  survey_id: string;
  user_id: string;
  respondent_email: string;
  assistant_id?: string;
  thread_id?: string;
  is_test: boolean;
  status: 'active' | 'completed' | 'abandoned';
  started_at: string;
  completed_at?: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface QuestionResponse {
  id: string;
  session_id: string;
  question_id: string;
  response_text: string;
  classified_answer: any;
  is_valid: boolean;
  created_at: string;
  updated_at: string;
}

// Function definitions for the assistant
const ASSISTANT_FUNCTIONS = [
  {
    type: "function" as const,
    function: {
      name: "classify_answer",
      description: "Classify user's response to match question type (MCQ option or rating value)",
      parameters: {
        type: "object",
        properties: {
          question_id: {
            type: "string",
            description: "The ID of the question being answered"
          },
          user_response: {
            type: "string",
            description: "The user's raw response text"
          },
          question_type: {
            type: "string",
            enum: ["mcq", "rating", "text", "yes_no"],
            description: "The type of question"
          },
          options: {
            type: "array",
            items: { type: "string" },
            description: "Available options for MCQ questions"
          },
          rating_start: {
            type: "number",
            description: "Start value for rating questions"
          },
          rating_end: {
            type: "number",
            description: "End value for rating questions"
          }
        },
        required: ["question_id", "user_response", "question_type"]
      }
    }
  },
  {
    type: "function" as const,
    function: {
      name: "validate_response",
      description: "Validate user responses for specific data types (email, phone, URL)",
      parameters: {
        type: "object",
        properties: {
          response: {
            type: "string",
            description: "The response to validate"
          },
          validation_type: {
            type: "string",
            enum: ["email", "phone", "url"],
            description: "Type of validation to perform"
          }
        },
        required: ["response", "validation_type"]
      }
    }
  },
  {
    type: "function" as const,
    function: {
      name: "save_response",
      description: "Save user's response to a specific question",
      parameters: {
        type: "object",
        properties: {
          session_id: {
            type: "string",
            description: "The chat session ID"
          },
          question_id: {
            type: "string",
            description: "The question ID"
          },
          response_text: {
            type: "string",
            description: "User's raw response"
          },
          classified_answer: {
            type: "object",
            description: "Processed/classified answer"
          },
          is_valid: {
            type: "boolean",
            description: "Whether the response is valid"
          }
        },
        required: ["session_id", "question_id", "response_text", "classified_answer", "is_valid"]
      }
    }
  },
  {
    type: "function" as const,
    function: {
      name: "end_survey",
      description: "Mark the survey as completed",
      parameters: {
        type: "object",
        properties: {
          session_id: {
            type: "string",
            description: "The chat session ID"
          },
          reason: {
            type: "string",
            enum: ["completed", "user_requested", "abandoned"],
            description: "Reason for ending the survey"
          }
        },
        required: ["session_id", "reason"]
      }
    }
  }
];

export class SurveyAssistant {
  private assistantId?: string;

  async createAssistant(surveyData: any): Promise<string> {
    const { survey, questions, demographics, profileInfo } = surveyData;
    
    console.log('🤖 Creating assistant for survey:', survey.title);
    console.log('📊 Survey has:', questions.length, 'questions,', demographics.length, 'demographics,', profileInfo.length, 'profile items');
    
    const instructions = `You are a professional survey interviewer conducting a research study. Your goal is to collect responses to survey questions in a natural, conversational manner.

SURVEY CONTEXT: ${survey.context}

SURVEY QUESTIONS:
${questions.map((q: any, i: number) => `${i + 1}. ${q.question_text} (Type: ${q.question_type}${q.options ? `, Options: ${q.options.join(', ')}` : ''}${q.rating_start ? `, Scale: ${q.rating_start}-${q.rating_end}` : ''})`).join('\n')}

DEMOGRAPHICS TO COLLECT:
${demographics.map((d: any) => `- ${d.demographic_type}`).join('\n')}

PROFILE INFO TO COLLECT:
${profileInfo.map((p: any) => `- ${p.profile_type}`).join('\n')}

INSTRUCTIONS:
1. Be conversational, friendly, and professional
2. Ask questions naturally, not like a form
3. Use follow-up questions to clarify responses
4. For MCQ questions, accept natural language responses and classify them
5. For rating questions, accept various formats (numbers, words like "good", "excellent")
6. Validate email addresses, phone numbers, and URLs when collecting profile info
7. If a user provides an answer to a different question, save it appropriately
8. Allow users to change their answers - update the database quietly
9. Use the save_response function after each answer is provided
10. Use end_survey when the survey is complete or user wants to stop
11. Keep the conversation engaging and show appreciation for their time

Start by introducing yourself and the survey purpose, then begin asking questions naturally.`;

    try {
      console.log('🔧 Creating OpenAI assistant...');
      const assistant = await openai.beta.assistants.create({
        name: `Survey Assistant - ${survey.title}`,
        instructions,
        model: "gpt-4-1106-preview",
        tools: ASSISTANT_FUNCTIONS
      });
      
      console.log('✅ Assistant created successfully:', assistant.id);
      this.assistantId = assistant.id;
      return assistant.id;
    } catch (error) {
      console.error('❌ Failed to create assistant:', error);
      throw new Error(`Failed to create assistant: ${error}`);
    }
  }

  async createThread(): Promise<string> {
    try {
      console.log('🧵 Creating OpenAI thread...');
      const thread = await openai.beta.threads.create();
      console.log('✅ Thread created successfully:', thread.id);
      return thread.id;
    } catch (error) {
      console.error('❌ Failed to create thread:', error);
      throw new Error(`Failed to create thread: ${error}`);
    }
  }

  async createThread(): Promise<string> {
    const thread = await openai.beta.threads.create();
    return thread.id;
  }

  async sendMessage(threadId: string, message: string, sessionId: string): Promise<string> {
    if (!this.assistantId) {
      throw new Error('Assistant not initialized');
    }

    console.log('🤖 Sending message to assistant:', { threadId, message, sessionId, assistantId: this.assistantId });

    // Add user message to thread
    try {
      await openai.beta.threads.messages.create(threadId, {
        role: "user",
        content: message
      });
      console.log('✅ User message added to thread');
    } catch (error) {
      console.error('❌ Failed to add user message to thread:', error);
      throw new Error(`Failed to add message to thread: ${error}`);
    }

    // Run the assistant
    let run;
    try {
      run = await openai.beta.threads.runs.create(threadId, {
        assistant_id: this.assistantId
      });
      console.log('✅ Assistant run created:', run.id);
    } catch (error) {
      console.error('❌ Failed to create assistant run:', error);
      throw new Error(`Failed to create assistant run: ${error}`);
    }

    // Wait for completion and handle function calls
    let runStatus;
    let attempts = 0;
    const maxAttempts = 60; // 60 seconds timeout
    
    while (attempts < maxAttempts) {
      try {
        runStatus = await openai.beta.threads.runs.retrieve(threadId, run.id);
        console.log(`🔄 Run status (attempt ${attempts + 1}):`, runStatus.status);
      } catch (error) {
        console.error('❌ Failed to retrieve run status:', error);
        throw new Error(`Failed to retrieve run status: ${error}`);
      }

      if (runStatus.status === 'completed') {
        console.log('✅ Assistant run completed');
        break;
      }

      if (runStatus.status === 'failed') {
        console.error('❌ Assistant run failed:', runStatus.last_error);
        throw new Error(`Assistant run failed: ${runStatus.last_error?.message || 'Unknown error'}`);
      }

      if (runStatus.status === 'cancelled') {
        console.error('❌ Assistant run was cancelled');
        throw new Error('Assistant run was cancelled');
      }

      if (runStatus.status === 'expired') {
        console.error('❌ Assistant run expired');
        throw new Error('Assistant run expired');
      }

      if (runStatus.status === 'requires_action' && runStatus.required_action?.type === 'submit_tool_outputs') {
        console.log('🔧 Function calls required:', runStatus.required_action.submit_tool_outputs.tool_calls.length);
        const toolOutputs = [];
        
        for (const toolCall of runStatus.required_action.submit_tool_outputs.tool_calls) {
          console.log('🔧 Handling function call:', toolCall.function.name);
          try {
            const output = await this.handleFunctionCall(toolCall, sessionId);
            console.log('✅ Function call result:', output);
            toolOutputs.push({
              tool_call_id: toolCall.id,
              output: JSON.stringify(output)
            });
          } catch (error) {
            console.error('❌ Function call failed:', error);
            toolOutputs.push({
              tool_call_id: toolCall.id,
              output: JSON.stringify({ success: false, error: error.message })
            });
          }
        }

        try {
          await openai.beta.threads.runs.submitToolOutputs(threadId, run.id, {
            tool_outputs: toolOutputs
          });
          console.log('✅ Tool outputs submitted');
        } catch (error) {
          console.error('❌ Failed to submit tool outputs:', error);
          throw new Error(`Failed to submit tool outputs: ${error}`);
        }
      }

      if (runStatus.status === 'running' || runStatus.status === 'requires_action') {
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      } else {
        break;
      }
    }

    if (attempts >= maxAttempts) {
      console.error('❌ Assistant run timed out');
      throw new Error('Assistant response timed out after 60 seconds');
    }

    // Get the assistant's response
    try {
      const messages = await openai.beta.threads.messages.list(threadId);
      console.log('📨 Retrieved messages:', messages.data.length);
      
      const lastMessage = messages.data[0];
      
      if (lastMessage && lastMessage.role === 'assistant' && lastMessage.content[0]?.type === 'text') {
        const response = lastMessage.content[0].text.value;
        console.log('✅ Assistant response received:', response.substring(0, 100) + '...');
        return response;
      } else {
        console.error('❌ No valid assistant response found');
        return "I apologize, but I'm having trouble processing your request right now. Could you please try again?";
      }
    } catch (error) {
      console.error('❌ Failed to retrieve assistant response:', error);
      return "I apologize, but I encountered an issue retrieving my response. Could you please try again?";
    }
  }

  private async handleFunctionCall(toolCall: any, sessionId: string): Promise<any> {
    try {
      const { name, arguments: args } = toolCall.function;
      console.log('🔧 Function call:', name, 'with args:', args);
      
      let parsedArgs;
      try {
        parsedArgs = JSON.parse(args);
      } catch (error) {
        console.error('❌ Failed to parse function arguments:', error);
        return { success: false, error: 'Invalid function arguments' };
      }

      switch (name) {
        case 'classify_answer':
          return await this.classifyAnswer(parsedArgs);
        
        case 'validate_response':
          return await this.validateResponse(parsedArgs);
        
        case 'save_response':
          return await this.saveResponse({ ...parsedArgs, session_id: sessionId });
        
        case 'end_survey':
          return await this.endSurvey({ ...parsedArgs, session_id: sessionId });
        
        default:
          console.error('❌ Unknown function:', name);
          return { success: false, error: 'Unknown function' };
      }
    } catch (error) {
      console.error('❌ Function call error:', error);
      return { success: false, error: error.message };
    }
  }

  private async classifyAnswer(args: any): Promise<any> {
    try {
      console.log('🔍 Classifying answer:', args);
      const { question_type, user_response, options, rating_start, rating_end } = args;

      switch (question_type) {
        case 'mcq':
          if (!options) return { success: false, error: 'No options provided' };
          
          // Use AI to match user response to closest option
          try {
            const matchResponse = await openai.chat.completions.create({
              model: 'gpt-3.5-turbo',
              messages: [{
                role: 'user',
                content: `Match this response "${user_response}" to the closest option from: ${options.join(', ')}. Return only the exact option text, or "NO_MATCH" if no reasonable match exists.`
              }],
              temperature: 0
            });
            
            const match = matchResponse.choices[0]?.message?.content?.trim();
            const isValidMatch = match && match !== 'NO_MATCH' && options.includes(match);
            
            return {
              success: true,
              classified_answer: {
                type: 'mcq',
                selected_option: isValidMatch ? match : null,
                original_response: user_response
              },
              is_valid: isValidMatch
            };
          } catch (error) {
            console.error('❌ AI matching failed, using fallback:', error);
            // Fallback to simple string matching
            const lowerResponse = user_response.toLowerCase();
            const matchedOption = options.find(option => 
              lowerResponse.includes(option.toLowerCase()) ||
              option.toLowerCase().includes(lowerResponse)
            );
            
            return {
              success: true,
              classified_answer: {
                type: 'mcq',
                selected_option: matchedOption || null,
                original_response: user_response
              },
              is_valid: !!matchedOption
            };
          }

        case 'rating':
          const numericValue = this.extractNumericRating(user_response, rating_start, rating_end);
          return {
            success: true,
            classified_answer: {
              type: 'rating',
              rating_value: numericValue,
              original_response: user_response
            },
            is_valid: numericValue !== null && numericValue >= rating_start && numericValue <= rating_end
          };

        case 'yes_no':
          const booleanValue = this.extractBooleanResponse(user_response);
          return {
            success: true,
            classified_answer: {
              type: 'yes_no',
              boolean_value: booleanValue,
              original_response: user_response
            },
            is_valid: booleanValue !== null
          };

        case 'text':
          return {
            success: true,
            classified_answer: {
              type: 'text',
              text_value: user_response.trim(),
              original_response: user_response
            },
            is_valid: user_response.trim().length > 0
          };

        default:
          return { success: false, error: 'Unknown question type' };
      }
    } catch (error) {
      console.error('❌ Classification error:', error);
      return { success: false, error: error.message };
    }
  }

  private async validateResponse(args: any): Promise<any> {
    try {
      console.log('✅ Validating response:', args);
      const { response, validation_type } = args;

      switch (validation_type) {
        case 'email':
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          return {
            success: true,
            is_valid: emailRegex.test(response),
            message: emailRegex.test(response) ? 'Valid email' : 'Please provide a valid email address'
          };

        case 'phone':
          const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
          const cleanPhone = response.replace(/[\s\-\(\)]/g, '');
          return {
            success: true,
            is_valid: phoneRegex.test(cleanPhone) && cleanPhone.length >= 10,
            message: phoneRegex.test(cleanPhone) && cleanPhone.length >= 10 ? 'Valid phone number' : 'Please provide a valid phone number'
          };

        case 'url':
          try {
            new URL(response);
            return {
              success: true,
              is_valid: true,
              message: 'Valid URL'
            };
          } catch {
            return {
              success: true,
              is_valid: false,
              message: 'Please provide a valid URL (including http:// or https://)'
            };
          }

        default:
          return { success: false, error: 'Unknown validation type' };
      }
    } catch (error) {
      console.error('❌ Validation error:', error);
      return { success: false, error: error.message };
    }
  }

  private async saveResponse(args: any): Promise<any> {
    try {
      console.log('💾 Saving response:', args);
      const { session_id, question_id, response_text, classified_answer, is_valid } = args;

      const { data, error } = await supabase
        .from('survey_question_responses')
        .upsert({
          session_id,
          question_id,
          response_text,
          classified_answer,
          is_valid,
          updated_at: new Date().toISOString()
        }, {
          onConflict: 'session_id,question_id'
        })
        .select()
        .single();

      if (error) {
        console.error('❌ Error saving response:', error);
        return { success: false, error: error.message };
      }

      console.log('✅ Response saved successfully');
      return { success: true, response_id: data.id };
    } catch (error) {
      console.error('❌ Error in saveResponse:', error);
      return { success: false, error: 'Failed to save response' };
    }
  }

  private async endSurvey(args: any): Promise<any> {
    try {
      console.log('🏁 Ending survey:', args);
      const { session_id, reason } = args;
      
      const status = reason === 'completed' ? 'completed' : 
                    reason === 'user_requested' ? 'abandoned' : 'abandoned';

      const { error } = await supabase
        .from('survey_chat_sessions')
        .update({
          status,
          completed_at: new Date().toISOString()
        })
        .eq('id', session_id);

      if (error) {
        console.error('❌ Error ending survey:', error);
        return { success: false, error: error.message };
      }

      console.log('✅ Survey ended successfully');
      return { success: true, status };
    } catch (error) {
      console.error('❌ Error in endSurvey:', error);
      return { success: false, error: 'Failed to end survey' };
    }
          toolOutputs.push({
            tool_call_id: toolCall.id,
            output: JSON.stringify(output)
          });
        }

        await openai.beta.threads.runs.submitToolOutputs(threadId, run.id, {
          tool_outputs: toolOutputs
        });
      }

      await new Promise(resolve => setTimeout(resolve, 1000));
      runStatus = await openai.beta.threads.runs.retrieve(threadId, run.id);
    }

    // Get the assistant's response
    const messages = await openai.beta.threads.messages.list(threadId);
    const lastMessage = messages.data[0];
    
    if (lastMessage.role === 'assistant' && lastMessage.content[0].type === 'text') {
      return lastMessage.content[0].text.value;
    }

    return "I apologize, but I encountered an issue. Could you please try again?";
  }

  private async handleFunctionCall(toolCall: any, sessionId: string): Promise<any> {
    const { name, arguments: args } = toolCall.function;
    const parsedArgs = JSON.parse(args);

    switch (name) {
      case 'classify_answer':
        return await this.classifyAnswer(parsedArgs);
      
      case 'validate_response':
        return await this.validateResponse(parsedArgs);
      
      case 'save_response':
        return await this.saveResponse({ ...parsedArgs, session_id: sessionId });
      
      case 'end_survey':
        return await this.endSurvey({ ...parsedArgs, session_id: sessionId });
      
      default:
        return { success: false, error: 'Unknown function' };
    }
  }

  private async classifyAnswer(args: any): Promise<any> {
    const { question_type, user_response, options, rating_start, rating_end } = args;

    switch (question_type) {
      case 'mcq':
        if (!options) return { success: false, error: 'No options provided' };
        
        // Use AI to match user response to closest option
        const matchResponse = await openai.chat.completions.create({
          model: 'gpt-3.5-turbo',
          messages: [{
            role: 'user',
            content: `Match this response "${user_response}" to the closest option from: ${options.join(', ')}. Return only the exact option text, or "NO_MATCH" if no reasonable match exists.`
          }],
          temperature: 0
        });
        
        const match = matchResponse.choices[0]?.message?.content?.trim();
        const isValidMatch = match && match !== 'NO_MATCH' && options.includes(match);
        
        return {
          success: true,
          classified_answer: {
            type: 'mcq',
            selected_option: isValidMatch ? match : null,
            original_response: user_response
          },
          is_valid: isValidMatch
        };

      case 'rating':
        const numericValue = this.extractNumericRating(user_response, rating_start, rating_end);
        return {
          success: true,
          classified_answer: {
            type: 'rating',
            rating_value: numericValue,
            original_response: user_response
          },
          is_valid: numericValue !== null && numericValue >= rating_start && numericValue <= rating_end
        };

      case 'yes_no':
        const booleanValue = this.extractBooleanResponse(user_response);
        return {
          success: true,
          classified_answer: {
            type: 'yes_no',
            boolean_value: booleanValue,
            original_response: user_response
          },
          is_valid: booleanValue !== null
        };

      case 'text':
        return {
          success: true,
          classified_answer: {
            type: 'text',
            text_value: user_response.trim(),
            original_response: user_response
          },
          is_valid: user_response.trim().length > 0
        };

      default:
        return { success: false, error: 'Unknown question type' };
    }
  }

  private extractNumericRating(response: string, min: number, max: number): number | null {
    // Extract numbers from response
    const numbers = response.match(/\d+/g);
    if (numbers) {
      const num = parseInt(numbers[0]);
      if (num >= min && num <= max) return num;
    }

    // Handle word-based ratings
    const lowerResponse = response.toLowerCase();
    const range = max - min;
    
    if (lowerResponse.includes('excellent') || lowerResponse.includes('perfect')) return max;
    if (lowerResponse.includes('very good') || lowerResponse.includes('great')) return Math.round(min + range * 0.8);
    if (lowerResponse.includes('good') || lowerResponse.includes('satisfied')) return Math.round(min + range * 0.6);
    if (lowerResponse.includes('okay') || lowerResponse.includes('average')) return Math.round(min + range * 0.5);
    if (lowerResponse.includes('poor') || lowerResponse.includes('bad')) return Math.round(min + range * 0.2);
    if (lowerResponse.includes('terrible') || lowerResponse.includes('awful')) return min;

    return null;
  }

  private extractBooleanResponse(response: string): boolean | null {
    const lowerResponse = response.toLowerCase();
    
    if (lowerResponse.includes('yes') || lowerResponse.includes('yeah') || 
        lowerResponse.includes('yep') || lowerResponse.includes('true') ||
        lowerResponse.includes('correct') || lowerResponse.includes('right')) {
      return true;
    }
    
    if (lowerResponse.includes('no') || lowerResponse.includes('nope') || 
        lowerResponse.includes('false') || lowerResponse.includes('wrong') ||
        lowerResponse.includes('incorrect')) {
      return false;
    }
    
    return null;
  }

  private async validateResponse(args: any): Promise<any> {
    const { response, validation_type } = args;

    switch (validation_type) {
      case 'email':
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return {
          success: true,
          is_valid: emailRegex.test(response),
          message: emailRegex.test(response) ? 'Valid email' : 'Please provide a valid email address'
        };

      case 'phone':
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        const cleanPhone = response.replace(/[\s\-\(\)]/g, '');
        return {
          success: true,
          is_valid: phoneRegex.test(cleanPhone) && cleanPhone.length >= 10,
          message: phoneRegex.test(cleanPhone) && cleanPhone.length >= 10 ? 'Valid phone number' : 'Please provide a valid phone number'
        };

      case 'url':
        try {
          new URL(response);
          return {
            success: true,
            is_valid: true,
            message: 'Valid URL'
          };
        } catch {
          return {
            success: true,
            is_valid: false,
            message: 'Please provide a valid URL (including http:// or https://)'
          };
        }

      default:
        return { success: false, error: 'Unknown validation type' };
    }
  }

  private async saveResponse(args: any): Promise<any> {
    try {
      const { session_id, question_id, response_text, classified_answer, is_valid } = args;

      const { data, error } = await supabase
        .from('survey_question_responses')
        .upsert({
          session_id,
          question_id,
          response_text,
          classified_answer,
          is_valid,
          updated_at: new Date().toISOString()
        }, {
          onConflict: 'session_id,question_id'
        })
        .select()
        .single();

      if (error) {
        console.error('Error saving response:', error);
        return { success: false, error: error.message };
      }

      return { success: true, response_id: data.id };
    } catch (error) {
      console.error('Error in saveResponse:', error);
      return { success: false, error: 'Failed to save response' };
    }
  }

  private async endSurvey(args: any): Promise<any> {
    try {
      const { session_id, reason } = args;
      
      const status = reason === 'completed' ? 'completed' : 
                    reason === 'user_requested' ? 'abandoned' : 'abandoned';

      const { error } = await supabase
        .from('survey_chat_sessions')
        .update({
          status,
          completed_at: new Date().toISOString()
        })
        .eq('id', session_id);

      if (error) {
        console.error('Error ending survey:', error);
        return { success: false, error: error.message };
      }

      return { success: true, status };
    } catch (error) {
      console.error('Error in endSurvey:', error);
      return { success: false, error: 'Failed to end survey' };
    }
  }
}

// Survey session management functions
export async function createSurveySession(
  surveyId: string, 
  userId: string,
  userEmail: string,
  isTest: boolean = false
): Promise<SurveySession> {
  // First try to get existing session
  const existingSession = await getSurveySession(surveyId, userId);
  if (existingSession) {
    return existingSession;
  }

  // Create new session
  const { data, error } = await supabase
    .from('survey_chat_sessions')
    .insert({
      survey_id: surveyId,
      user_id: userId,
      respondent_email: userEmail,
      is_test: isTest,
      status: 'active'
    })
    .select()
    .single();

  if (error) {
    throw new Error(`Failed to create session: ${error.message}`);
  }

  return data;
}

export async function getSurveySession(
  surveyId: string, 
  userId: string
): Promise<SurveySession | null> {
  const { data, error } = await supabase
    .from('survey_chat_sessions')
    .select('*')
    .eq('survey_id', surveyId)
    .eq('user_id', userId)
    .single();

  if (error && error.code !== 'PGRST116') {
    throw new Error(`Failed to get session: ${error.message}`);
  }

  return data;
}

export async function saveChatMessage(
  sessionId: string,
  role: 'user' | 'assistant',
  content: string
): Promise<ChatMessage> {
  const { data, error } = await supabase
    .from('survey_chat_messages')
    .insert({
      session_id: sessionId,
      role,
      content
    })
    .select()
    .single();

  if (error) {
    throw new Error(`Failed to save message: ${error.message}`);
  }

  return data;
}

export async function getChatHistory(sessionId: string): Promise<ChatMessage[]> {
  const { data, error } = await supabase
    .from('survey_chat_messages')
    .select('*')
    .eq('session_id', sessionId)
    .order('created_at', { ascending: true });

  if (error) {
    throw new Error(`Failed to get chat history: ${error.message}`);
  }

  return data || [];
}

export async function getSurveyForChat(surveyId: string): Promise<any> {
  const { data: survey, error: surveyError } = await supabase
    .from('surveys')
    .select(`
      *,
      survey_questions(*),
      survey_demographics(*),
      survey_profile_info(*)
    `)
    .eq('id', surveyId)
    .eq('is_active', true)
    .single();

  if (surveyError) {
    throw new Error(`Failed to get survey: ${surveyError.message}`);
  }

  return {
    survey,
    questions: survey.survey_questions.sort((a: any, b: any) => a.question_order - b.question_order),
    demographics: survey.survey_demographics.filter((d: any) => d.is_enabled),
    profileInfo: survey.survey_profile_info.filter((p: any) => p.is_enabled)
  };
}