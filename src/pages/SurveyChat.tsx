import React from 'react';
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
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
      const { data, error } = await supabase
        .from('surveys')
        .select('created_by, is_active')
        .eq('id', surveyId)
        .single();

      if (error) {
        console.error('Survey not found:', error);
        setError('Survey not found or not accessible');
        return;
      }

      if (!data.is_active) {
        setError('This survey is not currently active');
        return;
      }

      if (data.created_by === userId) {
        setIsCreator(true);
      }
    } catch (err) {
      console.error('Error checking survey creator:', err);
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
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Survey Error</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.history.back()}
            className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Show auth form only if:
  // 1. User is not authenticated AND it's not test mode, OR
  // 2. It's test mode but user is not authenticated or not the survey creator
  const shouldShowAuth = !user || (isTest && !isCreator);
  
  if (shouldShowAuth) {
    return <SurveyAuth surveyId={surveyId} onAuthenticated={handleAuthenticated} />;
  }

  // For test mode: if user is authenticated and is the creator, proceed to chat
  // For regular mode: if user is authenticated, proceed to chat
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
          <SurveyChatbot surveyId={surveyId} user={user} isTest={isTest} />
        </div>
      </div>
    </div>
  );
}