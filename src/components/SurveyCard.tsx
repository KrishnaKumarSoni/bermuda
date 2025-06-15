import React, { useState } from 'react'
import { FileText, Users, Calendar, Edit, Trash2, Share, BarChart3, Play } from 'lucide-react'
import { Survey, updateSurveyStatus, deleteSurvey } from '../lib/surveys'

interface SurveyCardProps {
  survey: Survey
  onEdit: (survey: Survey) => void
  onDelete: (surveyId: string) => void
  onStatusChange: (surveyId: string, isActive: boolean) => void
}

export default function SurveyCard({ survey, onEdit, onDelete, onStatusChange }: SurveyCardProps) {
  const [loading, setLoading] = useState(false)

  const handleStatusToggle = async () => {
    setLoading(true)
    try {
      await updateSurveyStatus(survey.id, !survey.is_active)
      onStatusChange(survey.id, !survey.is_active)
    } catch (error) {
      console.error('Failed to update survey status:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this survey? This action cannot be undone.')) {
      setLoading(true)
      try {
        await deleteSurvey(survey.id)
        onDelete(survey.id)
      } catch (error) {
        console.error('Failed to delete survey:', error)
      } finally {
        setLoading(false)
      }
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:border-gray-300 transition-colors">
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            {survey.title}
          </h3>
        </div>

        {/* Toggle Switch */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">
            {survey.is_active ? 'On' : 'Off'}
          </span>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={survey.is_active}
              onChange={handleStatusToggle}
              disabled={loading}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-600 disabled:opacity-50"></div>
          </label>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">
            {(survey as any).question_count || 0} questions
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <Users className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">
            {survey.response_count || 0} responses
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">
            {formatDate(survey.created_at)}
          </span>
        </div>
      </div>

      <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-lg">
        <p className="line-clamp-2">{survey.context}</p>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onEdit(survey)}
            className="p-2 text-gray-400 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
            title="Edit Survey"
          >
            <Edit className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => {/* TODO: Add share functionality */}}
            className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title="Share Survey"
          >
            <Share className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => {/* TODO: Add analytics functionality */}}
            className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
            title="View Analytics"
          >
            <BarChart3 className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => {/* TODO: Add test functionality */}}
            className="p-2 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
            title="Test Survey"
          >
            <Play className="w-4 h-4" />
          </button>
        </div>
        
        <button
          onClick={handleDelete}
          disabled={loading}
          className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
          title="Delete Survey"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}