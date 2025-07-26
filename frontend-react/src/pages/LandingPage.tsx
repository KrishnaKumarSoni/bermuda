import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, MessageCircle, BarChart3, Zap, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/stores/authStore';

export const LandingPage: React.FC = () => {
  const { user } = useAuthStore();

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-orange-100">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 pt-16 pb-24">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-heading font-bold text-gray-900 mb-6">
            Conversational
            <span className="text-primary-500 block">Forms Reimagined</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto font-body">
            Transform boring forms into engaging conversations. Bermuda uses AI to create 
            human-like chat experiences that get better responses and higher completion rates.
          </p>

          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            {user ? (
              <>
                <Link to="/create">
                  <Button size="lg">
                    <Zap className="w-5 h-5 mr-2" />
                    Create a Form
                  </Button>
                </Link>
                <Link to="/dashboard">
                  <Button variant="secondary" size="lg">
                    <BarChart3 className="w-5 h-5 mr-2" />
                    View Dashboard
                  </Button>
                </Link>
              </>
            ) : (
              <Link to="/create">
                <Button size="lg">
                  Get Started Free
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            )}
          </div>
        </div>

        {/* Hero Image/Demo */}
        <div className="mt-16 max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden">
            <div className="bg-gray-800 px-6 py-4 flex items-center space-x-3">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-gray-400 text-sm ml-4">Bermuda Chat</span>
            </div>
            <div className="p-8 space-y-4">
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 max-w-xs">
                  <p className="text-gray-800">Hi! I'm here to help you with our Customer Feedback Survey. What's your name?</p>
                </div>
              </div>
              <div className="flex justify-end">
                <div className="bg-primary-500 text-white rounded-2xl rounded-br-sm px-4 py-3 max-w-xs">
                  <p>I'm Sarah, nice to meet you!</p>
                </div>
              </div>
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 max-w-xs">
                  <p className="text-gray-800">Great to meet you Sarah! How would you rate your overall experience with our service?</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-white py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold text-gray-900 mb-4">
              Why Choose Bermuda?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Traditional forms are broken. We're fixing them with conversational AI.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-8">
              <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <MessageCircle className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-heading font-semibold text-gray-900 mb-4">
                Natural Conversations
              </h3>
              <p className="text-gray-600 font-body">
                AI-powered chat interface that feels like talking to a human. 
                Higher engagement and completion rates guaranteed.
              </p>
            </div>

            <div className="text-center p-8">
              <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Zap className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-heading font-semibold text-gray-900 mb-4">
                AI Form Generation
              </h3>
              <p className="text-gray-600 font-body">
                Just paste your requirements and watch AI generate a complete 
                conversational form in seconds.
              </p>
            </div>

            <div className="text-center p-8">
              <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <BarChart3 className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-heading font-semibold text-gray-900 mb-4">
                Smart Analytics
              </h3>
              <p className="text-gray-600 font-body">
                Extract structured data from conversations and export to CSV. 
                See what your respondents really think.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary-500 py-16">
        <div className="max-w-4xl mx-auto text-center px-6">
          <h2 className="text-3xl md:text-4xl font-heading font-bold text-white mb-4">
            Ready to Transform Your Forms?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Join thousands of creators building better survey experiences.
          </p>
          
          {!user && (
            <Link to="/create">
              <Button size="lg" variant="secondary">
                Start Creating for Free
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Trust Section */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto text-center px-6">
          <div className="flex items-center justify-center space-x-8 text-gray-400">
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5" />
              <span className="font-medium">Anonymous by Default</span>
            </div>
            <div className="w-px h-6 bg-gray-300"></div>
            <div className="flex items-center space-x-2">
              <MessageCircle className="w-5 h-5" />
              <span className="font-medium">GDPR Compliant</span>
            </div>
            <div className="w-px h-6 bg-gray-300"></div>
            <div className="flex items-center space-x-2">
              <Zap className="w-5 h-5" />
              <span className="font-medium">Real-time Sync</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};