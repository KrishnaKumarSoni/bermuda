import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, MessageCircle } from 'lucide-react';
import { 
  SurveyAssistant, 
  createSurveySession, 
  getSurveySession, 
  saveChatMessage, 
  getChatHistory, 
  getSurveyForChat,
  ChatMessage 
} from '../lib/surveyAssistant';
import { supabase } from '../lib/supabase';

interface SurveyChatbotProps {
  surveyId: string;
  user: any;
  isTest?: boolean;
  onClose?: () => void;
}

export default function SurveyChatbot({ surveyId, user, isTest = false, onClose }: SurveyChatbotProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [error, setError] = useState('');
  const [sessionId, setSessionId] = useState<string>('');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const assistantRef = useRef<SurveyAssistant>();
  const threadIdRef = useRef<string>('');

  useEffect(() => {
    initializeChatbot();
  }, [surveyId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeChatbot = async () => {
    try {
      console.log('🚀 Initializing chatbot for survey:', surveyId);
      setInitializing(true);
      setError('');

      if (!user?.id) {
        throw new Error('User not authenticated');
      }

      console.log('👤 User authenticated:', user.id, user.email);

      // Create session (fresh for test mode, existing for regular mode)
      let session;
      try {
        console.log(isTest ? '🆕 Creating fresh test session...' : '🔍 Getting or creating session...');
        session = await createSurveySession(surveyId, user.id, user.email, isTest);
        console.log('✅ Session ready:', session.id);
      } catch (error: any) {
        console.error('❌ Session creation failed:', error);
        throw error;
      }
      setSessionId(session.id);

      // Load chat history (should be empty for fresh test sessions)
      console.log('📜 Loading chat history...');
      const history = await getChatHistory(session.id);
      console.log('📜 Chat history loaded:', history.length, 'messages');
      setMessages(history);

      // For test mode, always initialize fresh assistant. For regular mode, check if assistant exists
      if (isTest || !session.assistant_id || !session.thread_id) {
        console.log(isTest ? '🤖 Initializing fresh test assistant...' : '🤖 Initializing new assistant...');
        const surveyData = await getSurveyForChat(surveyId);
        console.log('📊 Survey data loaded:', surveyData.survey.title);
        
        const assistant = new SurveyAssistant();
        const assistantId = await assistant.createAssistant(surveyData);
        console.log('🤖 Assistant created:', assistantId);
        const threadId = await assistant.createThread();
        console.log('🧵 Thread created:', threadId);

        // Update session with assistant details (only for non-test or new sessions)
        if (!isTest || !session.assistant_id) {
          await updateSessionAssistant(session.id, assistantId, threadId);
          console.log('✅ Session updated with assistant details');
        }
        
        assistantRef.current = assistant;
        threadIdRef.current = threadId;

        // Send initial message if no history
        if (history.length === 0) {
          console.log(isTest ? '💬 Sending fresh initial message...' : '💬 Sending initial message...');
          await sendInitialMessage(assistant, threadId, session.id);
        }
      } else {
        console.log('🔄 Restoring existing assistant...');
        // Restore existing assistant
        const surveyData = await getSurveyForChat(surveyId);
        const assistant = new SurveyAssistant();
        await assistant.createAssistant(surveyData); // This sets up the assistant with the same instructions
        console.log('✅ Assistant restored');
        
        assistantRef.current = assistant;
        threadIdRef.current = session.thread_id;
      }

      console.log('✅ Chatbot initialization complete');
    } catch (err: any) {
      console.error('Failed to initialize chatbot:', err);
      setError(err.message || 'Failed to initialize chat');
    } finally {
      setInitializing(false);
    }
  };

  const updateSessionAssistant = async (sessionId: string, assistantId: string, threadId: string) => {
    const { error } = await supabase
      .from('survey_chat_sessions')
      .update({ assistant_id: assistantId, thread_id: threadId })
      .eq('id', sessionId);

    if (error) {
      throw new Error(`Failed to update session: ${error.message}`);
    }
  };

  const sendInitialMessage = async (assistant: SurveyAssistant, threadId: string, sessionId: string) => {
    try {
      console.log('💬 Sending initial greeting...');
      const response = await assistant.sendMessage(threadId, "Hello! I'm ready to start the survey.", sessionId);
      console.log('✅ Initial response received');
      
      const assistantMessage = await saveChatMessage(sessionId, 'assistant', response);
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Failed to send initial message:', err);
      // Add a fallback message if AI fails
      const fallbackMessage = await saveChatMessage(sessionId, 'assistant', 
        "Hello! Welcome to this survey. I'm here to help guide you through the questions. Let's get started! What would you like to know about this survey?"
      );
      setMessages(prev => [...prev, fallbackMessage]);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading || !assistantRef.current) return;

    const userMessage = inputMessage.trim();
    console.log('📤 [USER MESSAGE] Sending:', userMessage);
    setInputMessage('');
    setLoading(true);

    try {
      // Save user message
      console.log('💾 [SAVE USER] Saving user message to database...');
      const userChatMessage = await saveChatMessage(sessionId, 'user', userMessage);
      setMessages(prev => [...prev, userChatMessage]);
      console.log('✅ [SAVE USER] User message saved successfully');

      // Get assistant response
      console.log('🤖 [GET RESPONSE] Getting assistant response...');
      const response = await assistantRef.current.sendMessage(
        threadIdRef.current, 
        userMessage, 
        sessionId
      );
      console.log('✅ [GET RESPONSE] Assistant response received:', response.substring(0, 50) + '...');

      // Save assistant response
      console.log('💾 [SAVE ASSISTANT] Saving assistant message to database...');
      const assistantMessage = await saveChatMessage(sessionId, 'assistant', response);
      setMessages(prev => [...prev, assistantMessage]);
      console.log('✅ [SAVE ASSISTANT] Assistant message saved successfully');

    } catch (err: any) {
      console.error('❌ [SEND MESSAGE ERROR] Failed to send message:', err);
      
      // Add error message to chat instead of showing error state
      console.log('💾 [SAVE ERROR] Saving error message to chat...');
      const errorMessage = await saveChatMessage(sessionId, 'assistant', 
        "I apologize, but I'm experiencing some technical difficulties. Could you please rephrase your response or try again?"
      );
      setMessages(prev => [...prev, errorMessage]);
      console.log('✅ [SAVE ERROR] Error message saved to chat');
    } finally {
      setLoading(false);
      console.log('🏁 [SEND MESSAGE] Message sending process completed');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (initializing) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center mx-auto mb-4">
            <Loader2 className="w-4 h-4 text-white animate-spin" />
          </div>
          <p className="text-gray-600">Initializing survey chat...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <MessageCircle className="w-8 h-8 text-red-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Chat Error</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={initializeChatbot}
            className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full max-h-[600px] bg-white border border-gray-200 rounded-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
            <MessageCircle className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Survey Assistant</h3>
            {isTest && (
              <span className="text-xs text-orange-600 bg-orange-100 px-2 py-1 rounded-full">
                Test Mode
              </span>
            )}
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-orange-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              <p className="text-xs opacity-70 mt-1">
                {new Date(message.created_at).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 p-3 rounded-lg">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Assistant is typing...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your response..."
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
            rows={1}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !inputMessage.trim()}
            className="bg-orange-600 text-white p-3 rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}