import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, MessageCircle, BarChart3, Calendar } from 'lucide-react';
import Layout from '../components/Layout';
import { supabase } from '../lib/supabase';

interface AnalyticsData {
  survey: any;
  sessions: any[];
  responses: any[];
  totalSessions: number;
  completedSessions: number;
  averageCompletionTime: number;
}

interface SurveyAnalyticsProps {
  user: any;
}

export default function SurveyAnalytics({ user }: SurveyAnalyticsProps) {
  const { surveyId } = useParams<{ surveyId: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [chatHistory, setChatHistory] = useState<any[]>([]);

  useEffect(() => {
    if (surveyId) {
      loadAnalytics();
    }
  }, [surveyId]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError('');

      // Get survey details
      const { data: survey, error: surveyError } = await supabase
        .from('surveys')
        .select(`
          *,
          survey_questions(*)
        `)
        .eq('id', surveyId)
        .eq('created_by', 'test-user-id')
        .single();

      if (surveyError) throw surveyError;

      // Get chat sessions
      const { data: sessions, error: sessionsError } = await supabase
        .from('survey_chat_sessions')
        .select('*')
        .eq('survey_id', surveyId)
        .order('started_at', { ascending: false });

      if (sessionsError) throw sessionsError;

      // Get responses
      const { data: responses, error: responsesError } = await supabase
        .from('survey_question_responses')
        .select(`
          *,
          survey_questions(*),
          survey_chat_sessions(respondent_fingerprint, is_test)
        `)
        .in('session_id', sessions?.map(s => s.id) || []);

      if (responsesError) throw responsesError;

      // Calculate analytics
      const totalSessions = sessions?.length || 0;
      const completedSessions = sessions?.filter(s => s.status === 'completed').length || 0;
      
      const completedSessionsWithTime = sessions?.filter(s => 
        s.status === 'completed' && s.started_at && s.completed_at
      ) || [];
      
      const averageCompletionTime = completedSessionsWithTime.length > 0
        ? completedSessionsWithTime.reduce((acc, session) => {
            const start = new Date(session.started_at).getTime();
            const end = new Date(session.completed_at).getTime();
            return acc + (end - start);
          }, 0) / completedSessionsWithTime.length / 1000 / 60 // Convert to minutes
        : 0;

      setData({
        survey,
        sessions: sessions || [],
        responses: responses || [],
        totalSessions,
        completedSessions,
        averageCompletionTime
      });

    } catch (err: any) {
      console.error('Failed to load analytics:', err);
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const loadChatHistory = async (sessionId: string) => {
    try {
      const { data, error } = await supabase
        .from('survey_chat_messages')
        .select('*')
        .eq('session_id', sessionId)
        .order('created_at', { ascending: true });

      if (error) throw error;
      setChatHistory(data || []);
      setSelectedSession(sessionId);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 1) return '< 1 min';
    if (minutes < 60) return `${Math.round(minutes)} min`;
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hours}h ${mins}m`;
  };

  if (loading) {
    return (
      <Layout user={user}>
        <div className="p-8">
          <div className="max-w-6xl mx-auto">
            <div className="text-center">
              <div className="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              </div>
              <p className="text-gray-600">Loading analytics...</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !data) {
    return (
      <Layout user={user}>
        <div className="p-8">
          <div className="max-w-6xl mx-auto">
            <div className="text-center">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Analytics</h3>
              <p className="text-gray-600 mb-4">{error}</p>
              <button
                onClick={() => navigate('/dashboard')}
                className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout user={user}>
      <div className="p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex items-center space-x-4 mb-8">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                Survey Analytics
              </h1>
              <p className="text-gray-600">{data.survey.title}</p>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Sessions</p>
                  <p className="text-2xl font-bold text-gray-900">{data.totalSessions}</p>
                </div>
                <Users className="w-8 h-8 text-blue-600" />
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Completed</p>
                  <p className="text-2xl font-bold text-gray-900">{data.completedSessions}</p>
                </div>
                <BarChart3 className="w-8 h-8 text-green-600" />
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Completion Rate</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {data.totalSessions > 0 ? Math.round((data.completedSessions / data.totalSessions) * 100) : 0}%
                  </p>
                </div>
                <BarChart3 className="w-8 h-8 text-orange-600" />
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Avg. Time</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatDuration(data.averageCompletionTime)}
                  </p>
                </div>
                <Calendar className="w-8 h-8 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Sessions List */}
            <div className="bg-white border border-gray-200 rounded-lg">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Chat Sessions</h3>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {data.sessions.map((session) => (
                  <div
                    key={session.id}
                    className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                      selectedSession === session.id ? 'bg-orange-50 border-orange-200' : ''
                    }`}
                    onClick={() => loadChatHistory(session.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">
                          {session.respondent_email || `User ${session.user_id?.slice(0, 8)}...`}
                        </p>
                        <p className="text-sm text-gray-600">
                          {new Date(session.started_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        {session.is_test && (
                          <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
                            Test
                          </span>
                        )}
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          session.status === 'completed' 
                            ? 'bg-green-100 text-green-800'
                            : session.status === 'active'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {session.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Chat History */}
            <div className="bg-white border border-gray-200 rounded-lg">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Chat History</h3>
              </div>
              <div className="max-h-96 overflow-y-auto p-4">
                {selectedSession ? (
                  <div className="space-y-4">
                    {chatHistory.map((message) => (
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
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Select a session to view chat history</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}