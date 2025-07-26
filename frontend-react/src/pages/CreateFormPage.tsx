import React from 'react';
import { Navigate } from 'react-router-dom';
import { Sparkles, FileText, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { FormBuilder } from '@/components/forms/FormBuilder';
import { useAuthStore } from '@/stores/authStore';
import { useFormStore } from '@/stores/formStore';

export const CreateFormPage: React.FC = () => {
  const { user, isLoading: authLoading } = useAuthStore();
  const { 
    currentForm, 
    isLoading, 
    error, 
    inferFormFromText,
    resetFormBuilder 
  } = useFormStore();

  const [textDump, setTextDump] = React.useState('');
  const [showBuilder, setShowBuilder] = React.useState(false);

  // Redirect to landing if not authenticated
  if (!authLoading && !user) {
    return <Navigate to="/" replace />;
  }

  // Show form builder if form exists
  if (currentForm || showBuilder) {
    return <FormBuilder />;
  }

  const handleGenerateForm = async () => {
    if (!textDump.trim()) {
      alert('Please enter some text to generate a form');
      return;
    }

    try {
      await inferFormFromText(textDump);
      setShowBuilder(true);
    } catch (error) {
      console.error('Failed to generate form:', error);
    }
  };

  const handleCreateBlank = () => {
    // Create a blank form
    const blankForm = {
      form_id: '',
      title: '',
      questions: [],
      demographics: [],
      created_at: new Date().toISOString(),
      creator_id: user?.uid || ''
    };
    
    // Set the form directly in the store
    useFormStore.getState().setCurrentForm(blankForm);
    setShowBuilder(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-orange-100">
      <div className="max-w-4xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-heading font-bold text-gray-900 mb-4">
            Create Your Form
          </h1>
          <p className="text-xl text-gray-600 font-body">
            Transform your ideas into engaging conversational forms
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* AI Generation Option */}
          <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-heading font-bold text-gray-900 mb-2">
                AI Generated
              </h3>
              <p className="text-gray-600 font-body">
                Paste your requirements and let AI create your form
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Describe your form or paste existing content
                </label>
                <textarea
                  value={textDump}
                  onChange={(e) => setTextDump(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none font-body"
                  rows={8}
                  placeholder="Example: I need a customer feedback survey asking about their recent purchase experience, delivery satisfaction, product quality, and likelihood to recommend. Also collect age, location, and how they heard about us."
                />
              </div>

              <Button 
                onClick={handleGenerateForm}
                isLoading={isLoading}
                disabled={!textDump.trim()}
                className="w-full"
                size="lg"
              >
                <Sparkles className="w-5 h-5 mr-2" />
                Generate with AI
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Manual Creation Option */}
          <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-r from-gray-500 to-gray-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-heading font-bold text-gray-900 mb-2">
                Start from Scratch
              </h3>
              <p className="text-gray-600 font-body">
                Build your form manually with full control
              </p>
            </div>

            <div className="space-y-6">
              <div className="space-y-3">
                <div className="flex items-center space-x-3 text-sm text-gray-600">
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  <span>Add unlimited questions</span>
                </div>
                <div className="flex items-center space-x-3 text-sm text-gray-600">
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  <span>5 question types available</span>
                </div>
                <div className="flex items-center space-x-3 text-sm text-gray-600">
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  <span>Drag & drop reordering</span>
                </div>
                <div className="flex items-center space-x-3 text-sm text-gray-600">
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  <span>Optional demographics</span>
                </div>
              </div>

              <Button 
                onClick={handleCreateBlank}
                variant="secondary"
                className="w-full"
                size="lg"
              >
                <FileText className="w-5 h-5 mr-2" />
                Start Building
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </div>
        </div>

        {/* Tips Section */}
        <div className="mt-16 bg-blue-50 rounded-2xl p-8 border border-blue-200">
          <h4 className="text-lg font-heading font-semibold text-blue-900 mb-4">
            💡 Pro Tips for Better Forms
          </h4>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800">
            <div className="space-y-2">
              <p>• Keep questions conversational and natural</p>
              <p>• Use multiple choice for standardized responses</p>
            </div>
            <div className="space-y-2">
              <p>• Add demographics sparingly to avoid fatigue</p>
              <p>• Test your form before sharing widely</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};