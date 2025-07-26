import React from 'react';
import { Bot, User } from 'lucide-react';
import { ChatMessage as ChatMessageType } from '@/types';
import { clsx } from 'clsx';

interface ChatMessageProps {
  message: ChatMessageType;
  isLast?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, isLast }) => {
  const isBot = message.sender === 'bot';

  return (
    <div className={clsx(
      'flex items-end space-x-3 animate-fade-in',
      isBot ? 'justify-start' : 'justify-end',
      isLast && 'mb-6'
    )}>
      {isBot && (
        <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}

      <div className={clsx(
        'max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-sm',
        isBot 
          ? 'bg-gray-100 text-gray-900 rounded-bl-sm' 
          : 'bg-primary-500 text-white rounded-br-sm'
      )}>
        <p className="text-sm font-body whitespace-pre-wrap">
          {message.text}
        </p>
        <p className={clsx(
          'text-xs mt-1 opacity-70',
          isBot ? 'text-gray-500' : 'text-primary-100'
        )}>
          {new Date(message.timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </p>
      </div>

      {!isBot && (
        <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  );
};