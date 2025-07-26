import { create } from 'zustand';
import { ChatState, ChatMessage, Form } from '@/types';
import { apiService } from '@/services/api';

interface ChatStore extends ChatState {
  // Actions
  sendMessage: (message: string, formId: string) => Promise<void>;
  initializeChat: (formId: string, sessionId?: string) => Promise<void>;
  setForm: (form: Form) => void;
  clearChat: () => void;
  
  // Enhanced features
  extractFormData: (formId: string) => Promise<any>;
  savePartialResponse: (formId: string) => Promise<void>;
  
  // Additional state
  messageCount: number;
  extractedData?: any;
  lastSaveTime?: number;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  // State
  messages: [],
  isLoading: false,
  sessionId: null,
  form: null,
  messageCount: 0,
  extractedData: undefined,
  lastSaveTime: undefined,

  sendMessage: async (message: string, formId: string) => {
    const { sessionId } = get();
    if (!sessionId) {
      throw new Error('No active chat session');
    }

    try {
      set({ isLoading: true });

      // Add user message immediately for optimistic updates
      const userMessage: ChatMessage = {
        id: `temp_${Date.now()}`,
        text: message,
        sender: 'user',
        timestamp: Date.now(),
        session_id: sessionId
      };

      set(state => ({
        messages: [...state.messages, userMessage]
      }));

      // Send to API for bot response (matching vanilla JS format)
      console.log('Sending message to API:', { form_id: formId, session_id: sessionId, message });
      
      const response = await fetch('https://us-central1-bermuda-01.cloudfunctions.net/api/chat-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          form_id: formId,
          session_id: sessionId,
          message: message,
          device_id: 'react-device',
          location: 'Unknown'
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('API Response:', result);

      // Add bot response directly to messages array (skip Firebase for now)
      if (result.response) {
        console.log('Adding bot response to messages:', result.response);
        
        const botMessage: ChatMessage = {
          id: `bot_${Date.now()}`,
          text: result.response,
          sender: 'bot',
          timestamp: Date.now(),
          session_id: sessionId
        };

        set(state => ({
          messages: [...state.messages, botMessage]
        }));
      } else {
        console.error('No response field in API result:', result);
      }

      set({ isLoading: false });
      
      // Increment message count for partial saves
      const state = get();
      const newMessageCount = state.messageCount + 2; // user + bot message
      set({ messageCount: newMessageCount });
      
      // Auto-save every 5 messages
      if (newMessageCount % 5 === 0) {
        await get().savePartialResponse(formId);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      set({ isLoading: false });
      
      // Remove optimistic message on error
      set(state => ({
        messages: state.messages.filter(msg => msg.id !== `temp_${Date.now()}`)
      }));
      
      throw error;
    }
  },

  initializeChat: async (formId: string, providedSessionId?: string) => {
    try {
      console.log('Initializing chat with formId:', formId);
      set({ isLoading: true });

      // Load form data
      console.log('Loading form data...');
      const form = await apiService.getForm(formId);
      console.log('Form loaded:', form);
      
      // Generate simple session ID like vanilla JS version
      const generateSessionId = () => {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
          const r = Math.random() * 16 | 0;
          const v = c == 'x' ? r : (r & 0x3 | 0x8);
          return v.toString(16);
        });
      };
      
      const sessionId = providedSessionId || generateSessionId();
      
      // Add initial bot message directly to state
      const initialMessage = `Hi! I'm here to help you with "${form.title}". Let's get started - just tell me a bit about yourself and answer the questions naturally.`;
      
      const botMessage: ChatMessage = {
        id: `initial_${Date.now()}`,
        text: initialMessage,
        sender: 'bot',
        timestamp: Date.now() - 1000, // Make it slightly older than user messages
        session_id: sessionId
      };

      set({
        form,
        sessionId,
        messages: [botMessage],
        isLoading: false
      });
    } catch (error) {
      console.error('Failed to initialize chat:', error);
      set({ isLoading: false });
      throw error;
    }
  },

  setForm: (form: Form) => set({ form }),

  clearChat: () => set({
    messages: [],
    sessionId: null,
    form: null,
    isLoading: false,
    messageCount: 0,
    extractedData: undefined,
    lastSaveTime: undefined
  }),

  extractFormData: async (formId: string) => {
    const { sessionId, messages, form } = get();
    if (!sessionId) {
      throw new Error('No active chat session');
    }

    if (!form) {
      throw new Error('No form data available');
    }

    try {
      // Convert messages to transcript format expected by API
      const transcript = messages.map(message => ({
        role: message.sender === 'user' ? 'user' : 'assistant',
        text: message.text,
        timestamp: new Date(message.timestamp).toISOString()
      }));

      // Convert form to questions_json format expected by API
      const questions_json = {
        questions: form.questions.map(q => ({
          question: q.text,
          type: q.type,
          enabled: q.enabled || true,
          options: q.options || undefined
        })),
        demographics: form.demographics.map(demo => ({
          question: demo,
          type: 'text',
          enabled: true
        }))
      };

      console.log('Extracting form data with:', { sessionId, transcript, questions_json });

      const response = await fetch('https://us-central1-bermuda-01.cloudfunctions.net/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          transcript: transcript,
          questions_json: questions_json
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Extract API Error:', response.status, errorText);
        throw new Error(`Failed to extract form data: ${response.status}`);
      }

      const extractedData = await response.json();
      console.log('Extracted data:', extractedData);
      
      set({ extractedData });
      return extractedData;
    } catch (error) {
      console.error('Failed to extract form data:', error);
      throw error;
    }
  },

  savePartialResponse: async (formId: string) => {
    const { sessionId, extractedData } = get();
    if (!sessionId) return;

    try {
      // Extract current data from chat transcript
      await get().extractFormData(formId);
      
      // Update last save time
      set({ lastSaveTime: Date.now() });
      
      console.log('Partial response saved at:', new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Failed to save partial response:', error);
      // Don't throw error for partial saves to avoid disrupting chat flow
    }
  },

}));