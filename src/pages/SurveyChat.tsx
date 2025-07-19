import React from 'react';
import { useParams } from 'react-router-dom';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import SurveyChatbot from '../components/SurveyChatbot';

export default function SurveyChat() {
  const { surveyId } = useParams<{ surveyId: string }>();
  const isTest = new URLSearchParams(window.location.search).get('test') === 'true';
  
  // Mock user for testing
  const user = {
    id: 'test-user-id',
    email: 'test@example.com'
  };

  if (!surveyId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Survey Not Found</h1>
          <p className="text-gray-600">The survey you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-4">
        <div className="mb-6">
          <button
            onClick={() => window.history.back()}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm">
          <div className="p-4 border-b border-gray-200 bg-blue-50">
            <h2 className="font-semibold text-gray-900">Survey Chat</h2>
            <p className="text-sm text-gray-600">
              {isTest ? 'Test Mode' : 'Survey Participation'} • 
              Testing as: {user.email}
            </p>
          </div>
          <SurveyChatbot surveyId={surveyId} user={user} isTest={isTest} />
        </div>
      </div>
    </div>
  );
}