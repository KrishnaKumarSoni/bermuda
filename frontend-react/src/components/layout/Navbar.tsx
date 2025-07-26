import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, PlusCircle, BarChart3 } from 'lucide-react';
import { AuthButton } from '@/components/auth/AuthButton';
import { useAuthStore } from '@/stores/authStore';
import { clsx } from 'clsx';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { user } = useAuthStore();

  const navItems = [
    { path: '/', label: 'Home', icon: Home, public: true },
    { path: '/create', label: 'Create', icon: PlusCircle, public: false },
    { path: '/dashboard', label: 'Dashboard', icon: BarChart3, public: false }
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="fixed top-6 left-1/2 transform -translate-x-1/2 z-50">
      <div className="bg-white/95 backdrop-blur-sm rounded-full shadow-lg border border-gray-200 px-4 py-2">
        <div className="flex items-center space-x-6">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-sm">B</span>
            </div>
            <span className="font-heading font-bold text-gray-900 hidden sm:inline">
              Bermuda
            </span>
          </Link>

          {/* Navigation Items */}
          <div className="flex items-center space-x-4">
            {navItems.map((item) => {
              // Show public items always, private items only when authenticated
              if (!item.public && !user) return null;
              
              const Icon = item.icon;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={clsx(
                    'flex items-center space-x-1 px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
                    isActive(item.path)
                      ? 'bg-primary-500 text-white'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Auth Section */}
          <div className="border-l border-gray-200 pl-4">
            <AuthButton />
          </div>
        </div>
      </div>
    </nav>
  );
};