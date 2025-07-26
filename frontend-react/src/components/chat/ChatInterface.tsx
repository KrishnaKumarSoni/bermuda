import React, { useEffect, useRef } from 'react';
import { AlertTriangle, Wifi, WifiOff } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { Loading } from '@/components/ui/Loading';
import { useChatStore } from '@/stores/chatStore';
import { clsx } from 'clsx';

interface ChatInterfaceProps {
  formId: string;
  sessionId?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  formId, 
  sessionId 
}) => {
  const {
    messages,
    isLoading,
    form,
    sendMessage,
    initializeChat,
    clearChat
  } = useChatStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isOnline, setIsOnline] = React.useState(navigator.onLine);
  const [error, setError] = React.useState<string | null>(null);

  // Initialize chat when component mounts
  useEffect(() => {
    const initialize = async () => {
      try {
        await initializeChat(formId, sessionId);
      } catch (error) {
        console.error('Failed to initialize chat:', error);
        setError('Failed to load form. Please try refreshing the page.');
      }
    };

    initialize();

    // Cleanup on unmount
    return () => {
      clearChat();
    };
  }, [formId, sessionId, initializeChat, clearChat]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleSendMessage = async (message: string) => {
    try {
      setError(null);
      await sendMessage(message, formId);
    } catch (error) {
      console.error('Failed to send message:', error);
      setError('Failed to send message. Please try again.');
    }
  };

  if (error && !form) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Something went wrong
          </h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            Refresh Page
          </button>
        </div>
      </div>
    );
  }

  if (!form) {
    return <Loading size="lg" />;
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-200 bg-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-heading font-bold text-gray-900">
              {form.title}
            </h2>
            <div className="flex items-center space-x-2 mt-1">
              {isOnline ? (
                <Wifi className="w-4 h-4 text-green-500" />
              ) : (
                <WifiOff className="w-4 h-4 text-red-500" />
              )}
              <span className={clsx(
                'text-sm',
                isOnline ? 'text-green-600' : 'text-red-600'
              )}>
                {isOnline ? 'Connected' : 'Offline'}
              </span>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-sm text-gray-500">
              {messages.filter(m => m.sender === 'user').length} responses
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && !isLoading ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">👋</span>
            </div>
            <p className="text-gray-600 font-body">
              Welcome! I'll guide you through this form.
            </p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage
                key={message.id}
                message={message}
                isLast={index === messages.length - 1}
              />
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  </div>
                  <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex-shrink-0 bg-red-50 border-t border-red-200 px-6 py-3">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      {/* Input */}
      <div className="flex-shrink-0">
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          disabled={!isOnline}
        />
      </div>
    </div>
  );
};