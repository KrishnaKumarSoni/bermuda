import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { ChatInterface } from '@/components/chat/ChatInterface';

export const ChatPage: React.FC = () => {
  const { formId } = useParams<{ formId: string }>();

  if (!formId) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="fixed inset-0 bg-gray-50 pt-20">
      <div className="h-full max-w-4xl mx-auto bg-white shadow-lg">
        <ChatInterface formId={formId} />
      </div>
    </div>
  );
};
