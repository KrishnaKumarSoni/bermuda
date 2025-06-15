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
  const [isCreator, setIsCreator] = useState(false);
  const [error, setError] = useState('');
  const [surveyData, setSurveyData] = useState<any>(null);
  const [debugInfo, setDebugInfo] = useState<any>(null);

  useEffect(() => {
    initializeAuth();
  }, [surveyId, isTest]);

  const initializeAuth = async () => {
    try {
      // Check if user is already authenticated
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user ?? null);
      
      // If it's test mode and user is authenticated, check if they're the survey creator
      if (isTest && session?.user && surveyId) {
        await checkIfCreator(session.user.id, surveyId);
      } else {
        setLoading(false);
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setUser(session?.user ?? null);
      
      // If it's test mode and user is authenticated, check if they're the survey creator
      if (isTest && session?.user && surveyId) {
        await checkIfCreator(session.user.id, surveyId);
      } else if (!isTest || !session?.user) {
        setLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, [isTest, surveyId]);

  const checkIfCreator = async (userId: string, surveyId: string) => {
    try {
      // First, let's check if the survey exists at all (without user restriction)
      const { data: surveyCheck, error: surveyCheckError } = await supabase
        .from('surveys')
        .select('id, title, created_by, is_active')
        .eq('id', surveyId)
        .single();

      setDebugInfo({
        surveyExists: !!surveyCheck,
        surveyData: surveyCheck,
        userId,
        isTest,
        error: surveyCheckError?.message
      });

      if (surveyCheckError) {
        console.error('Survey check error:', surveyCheckError);
        setError(`Survey not found: ${surveyCheckError.message}`);
        return;
      }

      if (!surveyCheck) {
        setError('Survey not found');
        return;
      }

      setSurveyData(surveyCheck);

      if (!surveyCheck.is_active) {
        setError('This survey is not currently active');
        return;
      }

      // Check if user is the creator
      if (surveyCheck.created_by === userId) {
        setIsCreator(true);
      }

      // For non-test mode, allow any authenticated user to access active surveys
      if (!isTest) {
        setIsCreator(true); // Allow access for regular survey participation
      }

    } catch (err) {
      console.error('Error checking survey creator:', err);
      setError('Failed to load survey');
    } finally {
      setLoading(false);
    }
  };

  // Alternative method to check survey without user restrictions
  const checkSurveyDirectly = async (surveyId: string) => {
    try {
      const { data, error } = await supabase
        .from('surveys')
        .select('*')
        .single();

      if (error) {
        console.error('Direct survey check error:', error);
        setError(`Survey access error: ${error.message}`);
        return;
      }

      setSurveyData(data);

      if (!data.is_active) {
        setError('This survey is not currently active');
        return;
      }

      // For test mode, check if user is creator
      if (isTest && user?.id && data.created_by === user.id) {
        setIsCreator(true);
      } else if (!isTest) {
        // For regular mode, allow any authenticated user
        setIsCreator(true);
      }

    } catch (err) {
      console.error('Error in direct survey check:', err);
      setError('Failed to load survey');
    } finally {
      setLoading(false);
    }
  };

  const handleAuthenticated = (authenticatedUser: any) => {
    setUser(authenticatedUser);
    setLoading(false);
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
          <p className="text-gray-600">Loading...</p>
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
            
            {debugInfo && (
              <div className="bg-gray-50 p-4 rounded-lg mb-4 text-left text-sm">
                <h3 className="font-semibold mb-2">Debug Information:</h3>
                <pre className="whitespace-pre-wrap text-xs">
                  {JSON.stringify(debugInfo, null, 2)}
                </pre>
              </div>
            )}
            
            <div className="space-y-2">
              <button
                onClick={() => checkSurveyDirectly(surveyId!)}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Try Direct Access
              </button>
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
  const shouldShowAuth = !user;
  
  if (shouldShowAuth) {
    return <SurveyAuth surveyId={surveyId} onAuthenticated={handleAuthenticated} />;
  }

  // If user is authenticated but not authorized for test mode
  if (isTest && !isCreator) {
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
            {surveyData && (
              <div className="bg-gray-50 p-4 rounded-lg mb-4 text-left text-sm">
                <p><strong>Survey:</strong> {surveyData.title}</p>
                <p><strong>Your ID:</strong> {user?.id}</p>
                <p><strong>Creator ID:</strong> {surveyData.created_by}</p>
              </div>
            )}
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
                Status: {surveyData.is_active ? 'Active' : 'Inactive'}
              </p>
            </div>
          )}
          <SurveyChatbot surveyId={surveyId} user={user} isTest={isTest} />
        </div>
      </div>
    </div>
  );
}