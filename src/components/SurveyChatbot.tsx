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
import { generateFingerprint } from '../lib/fingerprint';
import { supabase } from '../lib/supabase';

interface SurveyChatbotProps {
  surveyId: string;
  isTest?: boolean;
  onClose?: () => void;
}

export default function SurveyChatbot({ surveyId, isTest = false, onClose }: SurveyChatbotProps) {
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
      setInitializing(true);
      setError('');

      // Generate browser fingerprint
      const fingerprint = generateFingerprint();

      // Get or create session
      let session = await getSurveySession(surveyId, fingerprint);
      if (!session) {
        session = await createSurveySession(surveyId, fingerprint, isTest);
      }
      setSessionId(session.id);

      // Load chat history
      const history = await getChatHistory(session.id);
      setMessages(history);

      // Initialize assistant if needed
      if (!session.assistant_id || !session.thread_id) {
        const surveyData = await getSurveyForChat(surveyId);
        
        const assistant = new SurveyAssistant();
        const assistantId = await assistant.createAssistant(surveyData);
        const threadId = await assistant.createThread();

        // Update session with assistant details
        await updateSessionAssistant(session.id, assistantId, threadId);
        
        assistantRef.current = assistant;
        threadIdRef.current = threadId;

        // Send initial message if no history
        if (history.length === 0) {
          await sendInitialMessage(assistant, threadId, session.id);
        }
      } else {
        // Restore existing assistant
        const surveyData = await getSurveyForChat(surveyId);
        const assistant = new SurveyAssistant();
        await assistant.createAssistant(surveyData); // This sets up the assistant with the same instructions
        
        assistantRef.current = assistant;
        threadIdRef.current = session.thread_id;
      }

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
      const response = await assistant.sendMessage(threadId, "Hello! I'm ready to start the survey.", sessionId);
      
      const assistantMessage = await saveChatMessage(sessionId, 'assistant', response);
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Failed to send initial message:', err);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading || !assistantRef.current) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setLoading(true);

    try {
      // Save user message
      const userChatMessage = await saveChatMessage(sessionId, 'user', userMessage);
      setMessages(prev => [...prev, userChatMessage]);

      // Get assistant response
      const response = await assistantRef.current.sendMessage(
        threadIdRef.current, 
        userMessage, 
        sessionId
      );

      // Save assistant response
      const assistantMessage = await saveChatMessage(sessionId, 'assistant', response);
      setMessages(prev => [...prev, assistantMessage]);

    } catch (err: any) {
      console.error('Failed to send message:', err);
      setError(err.message || 'Failed to send message');
    } finally {
      setLoading(false);
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