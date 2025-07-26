import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-orange-100 flex items-center justify-center">
      <div className="text-center">
        <div className="w-32 h-32 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-8">
          <span className="text-6xl">🏝️</span>
        </div>
        
        <h1 className="text-4xl font-heading font-bold text-gray-900 mb-4">
          Lost in the Bermuda Triangle?
        </h1>
        
        <p className="text-xl text-gray-600 mb-8 font-body max-w-md mx-auto">
          This page seems to have disappeared into the void. Let's get you back to safety.
        </p>
        
        <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
          <Link to="/">
            <Button size="lg">
              <Home className="w-5 h-5 mr-2" />
              Go Home
            </Button>
          </Link>
          
          <Button variant="secondary" size="lg" onClick={() => window.history.back()}>
            <ArrowLeft className="w-5 h-5 mr-2" />
            Go Back
          </Button>
        </div>
      </div>
    </div>
  );
};