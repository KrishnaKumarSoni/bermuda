import React from 'react';
import {
  Play,
  BarChart3,
  Edit,
  Share,
  Trash2,
  Calendar,
  MessageCircle,
  ExternalLink,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Form } from '@/types';
import { clsx } from 'clsx';

interface FormCardProps {
  form: Form;
  onTest: (formId: string) => void;
  onViewResponses: (formId: string) => void;
  onEdit: (formId: string) => void;
  onShare: (formId: string) => void;
  onDelete: (formId: string) => void;
}

export const FormCard: React.FC<FormCardProps> = ({
  form,
  onTest,
  onViewResponses,
  onEdit,
  onShare,
  onDelete,
}) => {
  const createdDate = new Date(form.created_at);
  const isActive = form.is_active !== false;

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 hover:shadow-xl hover:border-primary-300 transition-all duration-300 group">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="font-heading font-bold text-lg text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
            {form.title}
          </h3>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <Calendar className="w-4 h-4" />
              <span>Created {createdDate.toLocaleDateString()}</span>
            </div>
            <div className="flex items-center space-x-1">
              <MessageCircle className="w-4 h-4" />
              <span>{form.questions?.length} questions</span>
            </div>
          </div>
        </div>

        {/* Status Indicator */}
        <div
          className={clsx(
            'w-3 h-3 rounded-full',
            isActive ? 'bg-green-500' : 'bg-gray-400'
          )}
        />
      </div>

      {/* Response Count */}
      <div className="mb-4">
        <div className="inline-flex items-center px-3 py-1 rounded-full bg-primary-100 text-primary-800 text-sm font-medium">
          <BarChart3 className="w-4 h-4 mr-1" />
          {form.response_count || 0} responses
        </div>
      </div>

      {/* Primary Actions */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => onTest(form.form_id)}
          className="text-sm"
        >
          <Play className="w-4 h-4 mr-1" />
          Test
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => onViewResponses(form.form_id)}
          className="text-sm"
        >
          <BarChart3 className="w-4 h-4 mr-1" />
          View
        </Button>
      </div>

      {/* Secondary Actions */}
      <div className="grid grid-cols-3 gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onEdit(form.form_id)}
          className="text-xs text-gray-600 hover:text-gray-900"
          title="Edit Form"
        >
          <Edit className="w-3 h-3 mr-1" />
          Edit
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => onShare(form.form_id)}
          className="text-xs text-gray-600 hover:text-gray-900"
          title="Share Form"
        >
          <Share className="w-3 h-3 mr-1" />
          Share
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete(form.form_id)}
          className="text-xs text-red-600 hover:text-red-700 hover:bg-red-50"
          title="Delete Form"
        >
          <Trash2 className="w-3 h-3 mr-1" />
          Delete
        </Button>
      </div>

      {/* Quick Stats */}
      {form.response_count && form.response_count > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-1">
            <p>Last response: {createdDate.toLocaleDateString()}</p>
            <div className="flex items-center justify-between">
              <span>Completion rate</span>
              <span className="font-medium text-green-600">85%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
