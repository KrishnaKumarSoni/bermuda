import React, { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { Toaster } from '@/components/ui/toaster';
import { useAuthStore } from '@/stores/authStore';

// Page components (we'll create these)
import { LandingPage } from '@/pages/LandingPage';
import { CreateFormPage } from '@/pages/CreateFormPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { ChatPage } from '@/pages/ChatPage';
import { NotFoundPage } from '@/pages/NotFoundPage';

function App() {
  const { initialize } = useAuthStore();

  useEffect(() => {
    // Initialize Firebase auth state listener
    const unsubscribe = initialize();
    
    // Cleanup on unmount
    return unsubscribe;
  }, [initialize]);

  return (
    <>
      <Layout>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/create" element={<CreateFormPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/form/:formId" element={<ChatPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Layout>
      <Toaster />
    </>
  );
}

export default App;