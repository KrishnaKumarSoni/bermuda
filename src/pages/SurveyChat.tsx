import React from 'react';
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import SurveyChatbot from '../components/SurveyChatbot';
import SurveyAuth from '../components/SurveyAuth';
import { supabase } from '../lib/supabase';

export default function SurveyChat() {
  const { surveyId } = useParams<{ surveyId: string }>();
  const isTest = new URLSearchParams(window.location.search).get('test') === 'true';
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [surveyData, setSurveyData] = useState<any>(null);

  useEffect(() => {
    initializeAuth();
  }, [surveyId]);

  const initializeAuth = async () => {
    try {
      setLoading(true);
      setError('');

      // Check if user is already authenticated
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user ?? null);
      
      // Check if survey exists and is accessible
      if (surveyId) {
        await checkSurvey(surveyId, session?.user);
      }

    } catch (error) {
      console.error('Error initializing auth:', error);
      setError('Failed to initialize survey');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setUser(session?.user ?? null);
      
      if (session?.user && surveyId) {
        await checkSurvey(surveyId, session.user);
      }
    });

    return () => subscription.unsubscribe();
  }, [surveyId]);

  const checkSurvey = async (surveyId: string, user: any) => {
    try {
      // Check if survey exists and is active (public access for basic info)
      const { data: survey, error: surveyError } = await supabase
        .from('surveys')
        .select('id, title, created_by, is_active')
        .eq('id', surveyId)
        .single();

      if (surveyError) {
        console.error('Survey check error:', surveyError);
        setError(`Survey not found: ${surveyError.message}`);
        return;
      }

      if (!survey) {
        setError('Survey not found');
        return;
      }

      setSurveyData(survey);

      if (!survey.is_active) {
        setError('This survey is not currently active');
        return;
      }

      // For test mode, check if user is the creator
      if (isTest && user) {
        if (survey.created_by !== user.id) {
          setError('Test mode is only available to the survey creator');
          return;
        }
      }

    } catch (err) {
      console.error('Error checking survey:', err);
      setError('Failed to load survey');
    }
  };

  const handleAuthenticated = (authenticatedUser: any) => {
    setUser(authenticatedUser);
    if (surveyId) {
      checkSurvey(surveyId, authenticatedUser);
    }
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center mx-auto mb-4">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p className="text-gray-600">Loading survey...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-lg p-8 border border-gray-200 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-8 h-8 text-red-400" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Survey Access Error</h1>
            <p className="text-gray-600 mb-4">{error}</p>
            
            <div className="space-y-2">
              <button
                onClick={() => window.history.back()}
                className="w-full bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"
              >
                Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show auth form if user is not authenticated
  if (!user) {
    return <SurveyAuth surveyId={surveyId} onAuthenticated={handleAuthenticated} />;
  }

  // If user is authenticated but not authorized for test mode
  if (isTest && surveyData && surveyData.created_by !== user.id) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-lg p-8 border border-gray-200 text-center">
            <div className="w-16 h-16 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-8 h-8 text-yellow-400" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Test Mode Access</h1>
            <p className="text-gray-600 mb-4">
              Test mode is only available to the survey creator.
            </p>
            <button
              onClick={() => window.location.href = `/survey/${surveyId}/chat`}
              className="w-full bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 mb-2"
            >
              Access Regular Survey
            </button>
            <button
              onClick={() => window.history.back()}
              className="w-full bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
            >
              Go Back
            </button>
          </div>
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
          {surveyData && (
            <div className="p-4 border-b border-gray-200 bg-blue-50">
              <h2 className="font-semibold text-gray-900">{surveyData.title}</h2>
              <p className="text-sm text-gray-600">
                {isTest ? 'Test Mode' : 'Survey Participation'} • 
                Signed in as: {user.email}
              </p>
            </div>
          )}
          <SurveyChatbot surveyId={surveyId} user={user} isTest={isTest} />
        </div>
      </div>
    </div>
  );
}