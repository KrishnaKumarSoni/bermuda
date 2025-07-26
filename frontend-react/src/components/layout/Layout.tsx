import React from 'react';
import { Navbar } from './Navbar';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      {/* Main content with top padding to account for fixed navbar */}
      <main className="pt-20">
        {children}
      </main>
    </div>
  );
};