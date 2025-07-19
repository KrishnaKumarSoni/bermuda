import React, { useState } from 'react'
import { ArrowLeft, Sparkles, Loader2, Plus } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { restrictToVerticalAxis } from '@dnd-kit/modifiers'
import Layout from '../components/Layout'
import QuestionCard from '../components/QuestionCard'
import AddQuestionModal from '../components/AddQuestionModal'
import DemographicsSection, { defaultDemographics } from '../components/DemographicsSection'
import ProfileSection, { defaultProfileInfo } from '../components/ProfileSection'
import { generateSurveyQuestions, SurveyQuestion } from '../lib/openai'
import { createSurvey, updateSurvey, getSurveyById, Survey } from '../lib/surveys'
import { useEffect } from 'react'

interface CreateSurveyProps {
  user: any
}

export default function CreateSurvey({ user }: CreateSurveyProps) {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEditing = Boolean(id)
  
  const [context, setContext] = useState('')
  const [title, setTitle] = useState('')
  const [questions, setQuestions] = useState<SurveyQuestion[]>([])
  const [demographics, setDemographics] = useState(defaultDemographics)
  const [profileInfo, setProfileInfo] = useState(defaultProfileInfo)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [questionsGenerated, setQuestionsGenerated] = useState(false)
  const [showAddQuestionModal, setShowAddQuestionModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [loadingExisting, setLoadingExisting] = useState(false)

  const sampleContext = "I want to understand how people consume content on the internet. How do they save content, share saved content, revisit saved content or how much are they interested in other people's saved content?"

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  // Load existing survey if editing
  useEffect(() => {
    if (isEditing && id) {
      loadExistingSurvey(id)
    }
  }, [id, isEditing])

  const loadExistingSurvey = async (surveyId: string) => {
    setLoadingExisting(true)
    try {
      const survey = await getSurveyById(surveyId)
      if (survey) {
        setTitle(survey.title)
        setContext(survey.context)
        setQuestions(survey.questions || [])
        setQuestionsGenerated(true)
        
        // Set demographics
        const enabledDemographics = survey.demographics?.map(d => d.demographic_type) || []
        setDemographics(demographics.map(d => ({
          ...d,
          enabled: enabledDemographics.includes(d.id)
        })))
        
        // Set profile info
        const enabledProfileInfo = survey.profile_info?.map(p => p.profile_type) || []
        setProfileInfo(profileInfo.map(p => ({
          ...p,
          enabled: enabledProfileInfo.includes(p.id)
        })))
      }
    } catch (error) {
      console.error('Failed to load survey:', error)
      setError('Failed to load survey')
    } finally {
      setLoadingExisting(false)
    }
  }

  const handleGenerateQuestions = async () => {
    if (!context.trim()) {
      setError('Please provide survey context')
      return
    }

    setLoading(true)
    setError('')

    try {
      const result = await generateSurveyQuestions(context)
      setTitle(result.title)
      setQuestions(result.questions)
      setQuestionsGenerated(true)
    } catch (err: any) {
      setError(err.message || 'Failed to generate questions. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleDragEnd = (event: any) => {
    const { active, over } = event

    if (active.id !== over.id) {
      setQuestions((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id)
        const newIndex = items.findIndex((item) => item.id === over.id)

        return arrayMove(items, oldIndex, newIndex)
      })
    }
  }

  const updateQuestion = (updatedQuestion: SurveyQuestion) => {
    setQuestions(questions.map(q => q.id === updatedQuestion.id ? updatedQuestion : q))
  }

  const deleteQuestion = (id: string) => {
    setQuestions(questions.filter(q => q.id !== id))
  }

  const addQuestion = (newQuestion: SurveyQuestion) => {
    setQuestions([...questions, newQuestion])
  }

  const toggleDemographic = (id: string) => {
    setDemographics(demographics.map(d => 
      d.id === id ? { ...d, enabled: !d.enabled } : d
    ))
  }

  const toggleProfileInfo = (id: string) => {
    setProfileInfo(profileInfo.map(p => 
      p.id === id ? { ...p, enabled: !p.enabled } : p
    ))
  }

  const handleCreateSurvey = async () => {
    if (!title.trim()) {
      setError('Please provide a survey title')
      return
    }
    
    if (questions.length === 0) {
      setError('Please add at least one question')
      return
    }

    setSaving(true)
    setError('')

    try {
      const surveyData = {
        title: title.trim(),
        context,
        questions,
        demographics: demographics.map(d => ({ id: d.id, enabled: d.enabled })),
        profileInfo: profileInfo.map(p => ({ id: p.id, enabled: p.enabled })),
      }

      if (isEditing && id) {
        await updateSurvey(id, surveyData)
      } else {
        await createSurvey(surveyData)
      }
      
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.message || `Failed to ${isEditing ? 'update' : 'create'} survey. Please try again.`)
    } finally {
      setSaving(false)
    }
  }

  const handleUseSample = () => {
    setContext(sampleContext)
  }

  if (loadingExisting) {
    return (
      <Layout user={user}>
        <div className="p-8">
          <div className="max-w-4xl mx-auto">
            <div className="text-center">
              <div className="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              </div>
              <p className="text-gray-600">Loading survey...</p>
            </div>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout user={user}>
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex items-center space-x-4 mb-8">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                {isEditing ? 'Edit Survey' : 'Create New Survey'}
              </h1>
              <p className="text-gray-600">
                Describe your survey context and let AI generate professional questions
              </p>
            </div>
          </div>

          {/* Context Input */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <label htmlFor="context" className="text-lg font-semibold text-gray-900" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                Survey Context
              </label>
              <button
                onClick={handleUseSample}
                className="text-sm text-orange-600 hover:text-orange-700 font-medium border border-orange-200 hover:border-orange-300 px-3 py-1 rounded-lg transition-colors"
              >
                Use Sample
              </button>
            </div>
            <textarea
              id="context"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
              placeholder="Describe what you want to survey about. For example: 'I want to understand customer satisfaction with our mobile app, focusing on usability, features, and overall experience. The target audience is existing users aged 25-45.'"
            />
            
            {error && (
              <div className="mt-4 text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                {error}
              </div>
            )}

            <button
              onClick={handleGenerateQuestions}
              disabled={loading || !context.trim() || (questionsGenerated && !isEditing)}
              className="mt-4 bg-orange-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-orange-700 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating Survey...</span>
                </>
              ) : questionsGenerated && !isEditing ? (
                <>
                  <Sparkles className="w-5 h-5" />
                  <span>Survey Generated</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  <span>Generate Survey</span>
                </>
              )}
            </button>
          </div>

          {/* Generated Survey Title */}
          {title && (
            <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                Survey Title
              </h3>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="Survey title will be generated automatically"
              />
            </div>
          )}

          {/* Generated Questions */}
          {questions.length > 0 && (
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                  Survey Questions
                </h2>
                <button
                  onClick={() => setShowAddQuestionModal(true)}
                  className="bg-orange-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-orange-700 transition-colors flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Question</span>
                </button>
              </div>
              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragEnd={handleDragEnd}
                modifiers={[restrictToVerticalAxis]}
              >
                <SortableContext items={questions.map(q => q.id)} strategy={verticalListSortingStrategy}>
                  {questions.map((question) => (
                    <QuestionCard
                      key={question.id}
                      question={question}
                      onUpdate={updateQuestion}
                      onDelete={deleteQuestion}
                    />
                  ))}
                </SortableContext>
              </DndContext>
            </div>
          )}

          {/* Demographics Section */}
          {questions.length > 0 && (
            <div className="mb-8">
              <DemographicsSection
                demographics={demographics}
                onToggle={toggleDemographic}
              />
            </div>
          )}

          {/* Profile Information Section */}
          {questions.length > 0 && (
            <div className="mb-8">
              <ProfileSection
                profileInfo={profileInfo}
                onToggle={toggleProfileInfo}
              />
            </div>
          )}

          {/* Create Survey Button */}
          {questions.length > 0 && (
            <div className="flex justify-center">
              <button
                onClick={handleCreateSurvey}
                disabled={saving}
                className="bg-orange-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>{isEditing ? 'Updating Survey...' : 'Creating Survey...'}</span>
                  </>
                ) : (
                  <span>{isEditing ? 'Update Survey' : 'Create Survey'}</span>
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Add Question Modal */}
      <AddQuestionModal
        isOpen={showAddQuestionModal}
        onClose={() => setShowAddQuestionModal(false)}
        onAdd={addQuestion}
      />
    </Layout>
  )
}