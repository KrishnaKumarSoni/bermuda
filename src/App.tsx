import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import CreateSurvey from './pages/CreateSurvey'
import SurveyChat from './pages/SurveyChat'
import SurveyAnalytics from './pages/SurveyAnalytics'

function App() {
  // Mock user for testing
  const user = {
    id: 'test-user-id',
    email: 'test@example.com'
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/dashboard" element={<Dashboard user={user} />} />
        <Route path="/create-survey" element={<CreateSurvey user={user} />} />
        <Route path="/create-survey/:id" element={<CreateSurvey user={user} />} />
        <Route 
          path="/survey/:surveyId/chat" 
          element={<SurveyChat />} 
        />
        <Route path="/survey/:surveyId/analytics" element={<SurveyAnalytics user={user} />} />
      </Routes>
    </Router>
  )
}

export default App
