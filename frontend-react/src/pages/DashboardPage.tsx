import React, { useEffect } from 'react';
import { Navigate, Link, useNavigate } from 'react-router-dom';
import { Plus, FileText, Search, Filter, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { FormCard } from '@/components/dashboard/FormCard';
import { Loading } from '@/components/ui/Loading';
import { ResponsesModal } from '@/components/forms/ResponsesModal';
import { useAuthStore } from '@/stores/authStore';
import { useFormStore } from '@/stores/formStore';
import { useToast } from '@/hooks/use-toast';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, isLoading: authLoading } = useAuthStore();
  const { forms, isLoading, error, loadForms, loadForm } = useFormStore();

  const [searchTerm, setSearchTerm] = React.useState('');
  const [showShareModal, setShowShareModal] = React.useState<string | null>(
    null
  );
  const [showResponsesModal, setShowResponsesModal] = React.useState<{
    formId: string;
    formTitle: string;
  } | null>(null);
  const { toast } = useToast();

  // Redirect to landing if not authenticated
  if (!authLoading && !user) {
    return <Navigate to="/" replace />;
  }

  // Load forms when component mounts
  useEffect(() => {
    if (user) {
      loadForms();
    }
  }, [user, loadForms]);

  // Filter forms based on search term
  const filteredForms = forms.filter((form) =>
    form.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleTestForm = (formId: string) => {
    navigate(`/form/${formId}`);
  };

  const handleViewResponses = (formId: string) => {
    const form = forms.find((f) => f.form_id === formId);
    if (form) {
      setShowResponsesModal({ formId, formTitle: form.title });
    }
  };

  const handleEditForm = async (formId: string) => {
    try {
      await loadForm(formId);
      navigate('/create');
    } catch (error) {
      console.error('Failed to load form for editing:', error);
    }
  };

  const handleShareForm = (formId: string) => {
    setShowShareModal(formId);
  };

  const handleDeleteForm = (formId: string) => {
    if (
      confirm(
        'Are you sure you want to delete this form? This action cannot be undone.'
      )
    ) {
      // TODO: Implement delete functionality
      console.log('Delete form:', formId);
    }
  };

  const copyShareLink = (formId: string) => {
    const shareUrl = `${window.location.origin}/form/${formId}`;
    navigator.clipboard.writeText(shareUrl);
    toast({
      title: 'Success',
      description: 'Share link copied to clipboard!',
    });
    setShowShareModal(null);
  };

  if (authLoading || isLoading) {
    return <Loading size="lg" />;
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-heading font-bold text-gray-900 mb-2">
            Your Forms
          </h1>
          <p className="text-gray-600 font-body">
            Manage and monitor your conversational forms
          </p>
        </div>

        <Link to="/create">
          <Button className="mt-4 sm:mt-0">
            <Plus className="w-4 h-4 mr-2" />
            Create New Form
          </Button>
        </Link>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">
                Total Forms
              </p>
              <p className="text-2xl font-bold text-gray-900">{forms.length}</p>
            </div>
            <FileText className="w-8 h-8 text-primary-500" />
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">
                Total Responses
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {forms.reduce(
                  (sum, form) => sum + (form.response_count || 0),
                  0
                )}
              </p>
            </div>
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 font-bold">📊</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">
                Avg. Completion
              </p>
              <p className="text-2xl font-bold text-gray-900">87%</p>
            </div>
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-bold">✓</span>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      {forms.length > 0 && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search forms..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            <div className="flex space-x-2">
              <Button variant="secondary" size="sm">
                <Filter className="w-4 h-4 mr-2" />
                Filter
              </Button>
              <Button variant="secondary" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Forms Grid */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {filteredForms.length === 0 ? (
        <div className="text-center py-16">
          {forms.length === 0 ? (
            <>
              <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <FileText className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-heading font-semibold text-gray-900 mb-2">
                No forms yet
              </h3>
              <p className="text-gray-600 mb-6 font-body">
                Create your first conversational form to get started
              </p>
              <Link to="/create">
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Form
                </Button>
              </Link>
            </>
          ) : (
            <>
              <h3 className="text-xl font-heading font-semibold text-gray-900 mb-2">
                No forms found
              </h3>
              <p className="text-gray-600 font-body">
                Try adjusting your search terms
              </p>
            </>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredForms.map((form) => (
            <FormCard
              key={form.form_id}
              form={form}
              onTest={handleTestForm}
              onViewResponses={handleViewResponses}
              onEdit={handleEditForm}
              onShare={handleShareForm}
              onDelete={handleDeleteForm}
            />
          ))}
        </div>
      )}

      {/* Share Modal */}
      {showShareModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-heading font-semibold text-gray-900 mb-4">
              Share Form
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Share Link
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    readOnly
                    value={`${window.location.origin}/form/${showShareModal}`}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm"
                  />
                  <Button
                    size="sm"
                    onClick={() => copyShareLink(showShareModal)}
                  >
                    Copy
                  </Button>
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <Button
                  variant="secondary"
                  onClick={() => setShowShareModal(null)}
                >
                  Close
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Responses Modal */}
      {showResponsesModal && (
        <ResponsesModal
          formId={showResponsesModal.formId}
          formTitle={showResponsesModal.formTitle}
          isOpen={true}
          onClose={() => setShowResponsesModal(null)}
        />
      )}
    </div>
  );
};
