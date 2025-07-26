import React from 'react';
import { Loader2 } from 'lucide-react';
import { clsx } from 'clsx';
import { LoadingProps } from '@/types';

export const Loading: React.FC<LoadingProps> = ({ 
  size = 'md', 
  color = 'text-primary-500' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  return (
    <div className="flex items-center justify-center p-4">
      <Loader2 className={clsx('animate-spin', sizeClasses[size], color)} />
    </div>
  );
};

export const FullPageLoading: React.FC = () => {
  return (
    <div className="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
      <div className="text-center">
        <Loader2 className="w-12 h-12 animate-spin text-primary-500 mx-auto mb-4" />
        <p className="text-gray-600 font-body">Loading...</p>
      </div>
    </div>
  );
};