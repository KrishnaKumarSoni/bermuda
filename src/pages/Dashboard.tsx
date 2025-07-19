import React from 'react'
import { useEffect, useState } from 'react'
import { Plus, BarChart3, FileText, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import SurveyCard from '../components/SurveyCard'
import { getUserSurveys, Survey } from '../lib/surveys'

interface DashboardProps {
  user: any
}

export default function Dashboard({ user }: DashboardProps) {
  const navigate = useNavigate()
  const [surveys, setSurveys] = useState<Survey[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadSurveys()
  }, [])

  const loadSurveys = async () => {
    try {
      const userSurveys = await getUserSurveys()
      setSurveys(userSurveys)
    } catch (err: any) {
      setError(err.message || 'Failed to load surveys')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSurvey = () => {
    navigate('/create-survey')
  }

  const handleEditSurvey = (survey: Survey) => {
    navigate(`/create-survey/${survey.id}`)
  }

  const handleDeleteSurvey = (surveyId: string) => {
    setSurveys(surveys.filter(s => s.id !== surveyId))
  }

  const handleStatusChange = (surveyId: string, isActive: boolean) => {
    setSurveys(surveys.map(s => 
      s.id === surveyId ? { ...s, is_active: isActive } : s
    ))
  }

  const totalResponses = surveys.reduce((sum, survey) => sum + (survey.response_count || 0), 0)
  const activeSurveys = surveys.filter(s => s.is_active).length
  const completionRate = surveys.length > 0 
    ? Math.round((totalResponses / (surveys.length * 10)) * 100) // Assuming 10 responses per survey as target
    : 0

  return (
    <Layout user={user}>
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              Welcome back, {user?.email?.split('@')[0]}!
            </h1>
            <p className="text-gray-600">
              Create and manage your AI-powered surveys
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Surveys</p>
                  <p className="text-2xl font-bold text-gray-900">{surveys.length}</p>
                </div>
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Responses</p>
                  <p className="text-2xl font-bold text-gray-900">{totalResponses}</p>
                </div>
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <Users className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Surveys</p>
                  <p className="text-2xl font-bold text-gray-900">{activeSurveys}</p>
                </div>
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Surveys Section */}
          {loading ? (
            <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
              <div className="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              </div>
              <p className="text-gray-600">Loading surveys...</p>
            </div>
          ) : error ? (
            <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
              <div className="w-16 h-16 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-red-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                Error loading surveys
              </h3>
              <p className="text-gray-600 mb-6">{error}</p>
              <button
                onClick={loadSurveys}
                className="bg-orange-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-orange-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : surveys.length === 0 ? (
            <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                No surveys yet
              </h3>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                Get started by creating your first AI-powered survey. Simply describe your research context and let our AI generate professional questions for you.
              </p>
              <button
                onClick={handleCreateSurvey}
                className="bg-orange-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-orange-700 transition-colors flex items-center space-x-2 mx-auto"
              >
                <Plus className="w-5 h-5" />
                <span>Create Survey</span>
              </button>
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                  Your Surveys
                </h2>
                <button
                  onClick={handleCreateSurvey}
                  className="bg-orange-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-orange-700 transition-colors flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Create Survey</span>
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {surveys.map((survey) => (
                  <SurveyCard
                    key={survey.id}
                    survey={survey}
                    onEdit={handleEditSurvey}
                    onDelete={handleDeleteSurvey}
                    onStatusChange={handleStatusChange}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}