import React from 'react';
import { LogIn, LogOut, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/stores/authStore';

export const AuthButton: React.FC = () => {
  const { user, isLoading, signInWithGoogle, signOut } = useAuthStore();

  if (isLoading) {
    return (
      <Button variant="ghost" size="sm" isLoading>
        Loading...
      </Button>
    );
  }

  if (user) {
    return (
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 text-sm text-gray-700">
          {user.photoURL ? (
            <img 
              src={user.photoURL} 
              alt={user.displayName || user.email || 'User'}
              className="w-6 h-6 rounded-full"
            />
          ) : (
            <User className="w-5 h-5" />
          )}
          <span className="hidden sm:inline">
            {user.displayName || user.email}
          </span>
        </div>
        <Button 
          variant="ghost" 
          size="sm"
          onClick={signOut}
          className="text-gray-600 hover:text-gray-900"
        >
          <LogOut className="w-4 h-4 mr-1" />
          Sign Out
        </Button>
      </div>
    );
  }

  return (
    <Button 
      variant="default" 
      size="sm"
      onClick={signInWithGoogle}
    >
      <LogIn className="w-4 h-4 mr-1" />
      Sign In
    </Button>
  );  
};