import React, { useState } from 'react'
import { X, Plus } from 'lucide-react'
import { SurveyQuestion } from '../lib/openai'

interface AddQuestionModalProps {
  isOpen: boolean
  onClose: () => void
  onAdd: (question: SurveyQuestion) => void
}

export default function AddQuestionModal({ isOpen, onClose, onAdd }: AddQuestionModalProps) {
  const [questionType, setQuestionType] = useState<'mcq' | 'text' | 'yes_no' | 'rating'>('mcq')
  const [questionText, setQuestionText] = useState('')
  const [options, setOptions] = useState(['Option 1', 'Option 2'])
  const [ratingStart, setRatingStart] = useState(1)
  const [ratingEnd, setRatingEnd] = useState(5)

  const questionTypes = [
    { value: 'mcq', label: 'Multiple Choice' },
    { value: 'text', label: 'Text Response' },
    { value: 'yes_no', label: 'Yes/No' },
    { value: 'rating', label: 'Rating Scale' },
  ]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!questionText.trim()) return

    const newQuestion: SurveyQuestion = {
      id: `manual_${Date.now()}`,
      type: questionType,
      question: questionText.trim(),
      ...(questionType === 'mcq' && { options: options.filter(opt => opt.trim()) }),
      ...(questionType === 'rating' && { ratingStart, ratingEnd }),
    }

    onAdd(newQuestion)
    handleClose()
  }

  const handleClose = () => {
    setQuestionText('')
    setOptions(['Option 1', 'Option 2'])
    setRatingStart(1)
    setRatingEnd(5)
    setQuestionType('mcq')
    onClose()
  }

  const addOption = () => {
    setOptions([...options, `Option ${options.length + 1}`])
  }

  const updateOption = (index: number, value: string) => {
    const newOptions = [...options]
    newOptions[index] = value
    setOptions(newOptions)
  }

  const removeOption = (index: number) => {
    if (options.length > 2) {
      setOptions(options.filter((_, i) => i !== index))
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            Add Question Manually
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Question Type
            </label>
            <select
              value={questionType}
              onChange={(e) => setQuestionType(e.target.value as any)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            >
              {questionTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Question Text
            </label>
            <textarea
              value={questionText}
              onChange={(e) => setQuestionText(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
              rows={3}
              placeholder="Enter your question..."
              required
            />
          </div>

          {questionType === 'mcq' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Options
              </label>
              <div className="space-y-2">
                {options.map((option, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className="text-gray-400 text-sm">{index + 1}.</span>
                    <input
                      type="text"
                      value={option}
                      onChange={(e) => updateOption(index, e.target.value)}
                      className="flex-1 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      placeholder={`Option ${index + 1}`}
                    />
                    {options.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeOption(index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addOption}
                  className="flex items-center space-x-2 text-orange-600 hover:text-orange-700 text-sm"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add option</span>
                </button>
              </div>
            </div>
          )}

          {questionType === 'rating' && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Value
                </label>
                <input
                  type="number"
                  min="1"
                  value={ratingStart}
                  onChange={(e) => setRatingStart(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Value
                </label>
                <input
                  type="number"
                  min={ratingStart}
                  value={ratingEnd}
                  onChange={(e) => setRatingEnd(Math.max(ratingStart, parseInt(e.target.value) || 5))}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
            >
              Add Question
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}