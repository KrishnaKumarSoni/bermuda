import React, { useState } from 'react'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { GripVertical, Trash2, Plus, X } from 'lucide-react'
import { SurveyQuestion } from '../lib/openai'

interface QuestionCardProps {
  question: SurveyQuestion
  onUpdate: (question: SurveyQuestion) => void
  onDelete: (id: string) => void
}

export default function QuestionCard({ question, onUpdate, onDelete }: QuestionCardProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedQuestion, setEditedQuestion] = useState(question)

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: question.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  const questionTypes = [
    { value: 'mcq', label: 'Multiple Choice' },
    { value: 'text', label: 'Text Response' },
    { value: 'yes_no', label: 'Yes/No' },
    { value: 'rating', label: 'Rating Scale' },
  ]

  const handleSave = () => {
    onUpdate(editedQuestion)
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditedQuestion(question)
    setIsEditing(false)
  }

  const addOption = () => {
    if (editedQuestion.type === 'mcq') {
      const newOptions = [...(editedQuestion.options || []), '']
      setEditedQuestion({ ...editedQuestion, options: newOptions })
    }
  }

  const updateOption = (index: number, value: string) => {
    if (editedQuestion.type === 'mcq' && editedQuestion.options) {
      const newOptions = [...editedQuestion.options]
      newOptions[index] = value
      setEditedQuestion({ ...editedQuestion, options: newOptions })
    }
  }

  const removeOption = (index: number) => {
    if (editedQuestion.type === 'mcq' && editedQuestion.options) {
      const newOptions = editedQuestion.options.filter((_, i) => i !== index)
      setEditedQuestion({ ...editedQuestion, options: newOptions })
    }
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="bg-white border border-gray-200 rounded-lg p-6 mb-4"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <button
            {...attributes}
            {...listeners}
            className="text-gray-400 hover:text-gray-600 cursor-grab active:cursor-grabbing"
          >
            <GripVertical className="w-5 h-5" />
          </button>
          
          <div className="px-3 py-2 bg-gray-100 rounded-lg text-sm font-medium text-gray-700">
            {questionTypes.find(t => t.value === editedQuestion.type)?.label}
          </div>
        </div>

        <button
          onClick={() => onDelete(question.id)}
          className="text-gray-400 hover:text-red-600"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      </div>

      <div className="space-y-4">
        {isEditing ? (
          <div>
            <textarea
              value={editedQuestion.question}
              onChange={(e) => setEditedQuestion({ ...editedQuestion, question: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
              rows={3}
              placeholder="Enter your question..."
            />
          </div>
        ) : (
          <div>
            <p className="text-lg font-medium text-gray-900 mb-2">{question.question}</p>
          </div>
        )}

        {/* Question type specific content */}
        {editedQuestion.type === 'mcq' && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Options:</label>
            {editedQuestion.options?.map((option, index) => (
              <div key={index} className="flex items-center space-x-2">
                <span className="text-gray-400 text-sm">{index + 1}.</span>
                {isEditing ? (
                  <>
                    <input
                      type="text"
                      value={option}
                      onChange={(e) => updateOption(index, e.target.value)}
                      className="flex-1 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      placeholder={`Option ${index + 1}`}
                    />
                    <button
                      onClick={() => removeOption(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </>
                ) : (
                  <span className="text-gray-700">{option}</span>
                )}
              </div>
            ))}
            {isEditing && (
              <button
                onClick={addOption}
                className="flex items-center space-x-2 text-orange-600 hover:text-orange-700 text-sm"
              >
                <Plus className="w-4 h-4" />
                <span>Add option</span>
              </button>
            )}
          </div>
        )}

        {editedQuestion.type === 'rating' && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start</label>
              {isEditing ? (
                <input
                  type="number"
                  min="1"
                  value={editedQuestion.ratingStart || 1}
                  onChange={(e) => setEditedQuestion({ 
                    ...editedQuestion, 
                    ratingStart: Math.max(1, parseInt(e.target.value) || 1)
                  })}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              ) : (
                <span className="text-gray-700">{question.ratingStart || 1}</span>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End</label>
              {isEditing ? (
                <input
                  type="number"
                  min={editedQuestion.ratingStart || 1}
                  value={editedQuestion.ratingEnd || 5}
                  onChange={(e) => setEditedQuestion({ 
                    ...editedQuestion, 
                    ratingEnd: Math.max(editedQuestion.ratingStart || 1, parseInt(e.target.value) || 5)
                  })}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              ) : (
                <span className="text-gray-700">{question.ratingEnd || 5}</span>
              )}
            </div>
          </div>
        )}

        {editedQuestion.type === 'yes_no' && (
          <div className="text-sm text-gray-600">
            Respondents will choose between Yes and No
          </div>
        )}

        {editedQuestion.type === 'text' && (
          <div className="text-sm text-gray-600">
            Respondents will provide a text response
          </div>
        )}
      </div>

      <div className="flex justify-end space-x-2 mt-4">
        {isEditing ? (
          <>
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
            >
              Save
            </button>
          </>
        ) : (
          <button
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 text-orange-600 hover:text-orange-700"
          >
            Edit
          </button>
        )}
      </div>
    </div>
  )
}