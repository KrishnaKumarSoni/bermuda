import React from 'react';
import { Plus, Save, Eye, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { QuestionCard } from './QuestionCard';
import { DemographicsSelector } from './DemographicsSelector';
import { useFormStore } from '@/stores/formStore';
import { useToast } from '@/hooks/use-toast';
import { Question, DEMOGRAPHIC_OPTIONS } from '@/types';
import { createDragHandlers } from '@/utils/dragdrop';
import { clsx } from 'clsx';

export const FormBuilder: React.FC = () => {
  const {
    currentForm,
    isLoading,
    isDirty,
    updateCurrentForm,
    updateQuestion,
    addQuestion,
    removeQuestion,
    reorderQuestions,
    saveForm,
    resetFormBuilder
  } = useFormStore();

  const [showPreview, setShowPreview] = React.useState(false);
  const { toast } = useToast();

  // Create drag & drop handlers
  const dragHandlers = createDragHandlers(reorderQuestions);

  if (!currentForm) {
    return null;
  }

  const handleAddQuestion = () => {
    const newQuestion: Question = {
      id: `q_${Date.now()}`,
      text: '',
      type: 'text',
      required: true,
      enabled: true
    };
    addQuestion(newQuestion);
  };

  const handleSaveForm = async () => {
    if (!currentForm.title.trim()) {
      toast({
        title: "Error",
        description: "Please enter a form title",
        variant: "destructive"
      });
      return;
    }

    if (currentForm.questions.length === 0) {
      toast({
        title: "Error",
        description: "Please add at least one question",
        variant: "destructive"
      });
      return;
    }

    // Validate questions
    const invalidQuestions = currentForm.questions.filter(q => !q.text.trim());
    if (invalidQuestions.length > 0) {
      toast({
        title: "Error",
        description: "Please fill in all question texts",
        variant: "destructive"
      });
      return;
    }

    try {
      const formId = await saveForm(currentForm);
      toast({
        title: "Success",
        description: `Form saved successfully! Form ID: ${formId}`
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save form. Please try again.",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            onClick={resetFormBuilder}
            className="text-gray-600"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-heading font-bold text-gray-900">
              Form Builder
            </h1>
            <p className="text-gray-600 mt-1">
              Design your conversational form
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <Button
            variant="secondary"
            onClick={() => setShowPreview(!showPreview)}
          >
            <Eye className="w-4 h-4 mr-2" />
            {showPreview ? 'Edit' : 'Preview'}
          </Button>
          
          <Button
            onClick={handleSaveForm}
            isLoading={isLoading}
            disabled={!isDirty || !currentForm.title.trim()}
          >
            <Save className="w-4 h-4 mr-2" />
            Save Form
          </Button>
        </div>
      </div>

      {showPreview ? (
        <FormPreview form={currentForm} />
      ) : (
        <div className="space-y-8">
          {/* Form Title */}
          <Card>
            <CardHeader>
              <CardTitle>Form Title</CardTitle>
            </CardHeader>
            <CardContent>
              <Input
                type="text"
                value={currentForm.title}
                onChange={(e) => updateCurrentForm({ title: e.target.value })}
                className="text-xl font-heading"
                placeholder="Enter your form title..."
              />
            </CardContent>
          </Card>

          {/* Demographics */}
          <Card>
            <CardHeader>
              <CardTitle>Demographics (Optional)</CardTitle>
            </CardHeader>
            <CardContent>
              <DemographicsSelector
                selected={currentForm.demographics}
                onChange={(demographics) => updateCurrentForm({ demographics })}
              />
            </CardContent>
          </Card>

          {/* Questions */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-heading font-semibold text-gray-900">
                Questions ({currentForm.questions.length})
              </h3>
              <Button onClick={handleAddQuestion}>
                <Plus className="w-4 h-4 mr-2" />
                Add Question
              </Button>
            </div>

            {currentForm.questions.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <p className="text-muted-foreground mb-4">No questions yet</p>
                  <Button onClick={handleAddQuestion}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Your First Question
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-6">
                {currentForm.questions.map((question, index) => (
                  <div
                    key={question.id}
                    draggable
                    onDragStart={(e) => dragHandlers.handleDragStart(e, index)}
                    onDragEnd={dragHandlers.handleDragEnd}
                    onDragOver={dragHandlers.handleDragOver}
                    onDragEnter={(e) => dragHandlers.handleDragEnter(e, index)}
                    onDragLeave={dragHandlers.handleDragLeave}
                    onDrop={(e) => dragHandlers.handleDrop(e, index)}
                    className="question-drag-container"
                  >
                    <QuestionCard
                      question={question}
                      index={index}
                      onUpdate={(updates) => updateQuestion(index, updates)}
                      onDelete={() => removeQuestion(index)}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Simple form preview component
const FormPreview: React.FC<{ form: any }> = ({ form }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl font-heading">
          {form.title}
        </CardTitle>
      </CardHeader>
      <CardContent>
      
      <div className="space-y-6">
        {form.questions.filter((q: Question) => q.enabled !== false).map((question: Question, index: number) => (
          <div key={question.id} className="border-b border-gray-200 pb-6 last:border-b-0">
            <h3 className="font-medium text-gray-900 mb-3">
              {index + 1}. {question.text}
              {question.required && <span className="text-red-500 ml-1">*</span>}
            </h3>
            
            {question.type === 'multiple_choice' && question.options && (
              <div className="space-y-2">
                {question.options.map((option, optionIndex) => (
                  <label key={optionIndex} className="flex items-center space-x-2">
                    <input type="radio" name={`q_${index}`} className="text-primary-600" />
                    <span className="text-gray-700">{option}</span>
                  </label>
                ))}
              </div>
            )}
            
            {question.type === 'yes_no' && (
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input type="radio" name={`q_${index}`} className="text-primary-600" />
                  <span className="text-gray-700">Yes</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input type="radio" name={`q_${index}`} className="text-primary-600" />
                  <span className="text-gray-700">No</span>
                </label>
              </div>
            )}
            
            {question.type === 'text' && (
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Your answer..."
                rows={3}
              />
            )}
            
            {question.type === 'number' && (
              <input
                type="number"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Enter a number..."
              />
            )}
            
            {question.type === 'rating' && (
              <div className="flex space-x-2">
                {[1, 2, 3, 4, 5].map(rating => (
                  <button
                    key={rating}
                    className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-primary-50 hover:border-primary-300"
                  >
                    {rating}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      </CardContent>
    </Card>
  );
};