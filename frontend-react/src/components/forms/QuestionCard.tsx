import React from 'react';
import { 
  GripVertical, 
  Type, 
  List, 
  CheckCircle, 
  Star, 
  Hash, 
  Edit3, 
  Trash2,
  Plus,
  X
} from 'lucide-react';
import { Question, QUESTION_TYPES } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent } from '@/components/ui/card';
import { clsx } from 'clsx';

interface QuestionCardProps {
  question: Question;
  index: number;
  onUpdate: (updates: Partial<Question>) => void;
  onDelete: () => void;
  isDragging?: boolean;
}

const getQuestionIcon = (type: string) => {
  const iconMap = {
    text: Type,
    multiple_choice: List,
    yes_no: CheckCircle,
    rating: Star,
    number: Hash
  };
  return iconMap[type as keyof typeof iconMap] || Type;
};

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  index,
  onUpdate,
  onDelete,
  isDragging = false
}) => {
  const [isEditing, setIsEditing] = React.useState(false);
  const [localText, setLocalText] = React.useState(question.text);
  const [localOptions, setLocalOptions] = React.useState(question.options || []);

  const Icon = getQuestionIcon(question.type);
  const currentType = QUESTION_TYPES.find(t => t.value === question.type);

  const handleSaveText = () => {
    onUpdate({ text: localText });
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setLocalText(question.text);
    setIsEditing(false);
  };

  const handleAddOption = () => {
    const newOptions = [...localOptions, ''];
    setLocalOptions(newOptions);
    onUpdate({ options: newOptions });
  };

  const handleUpdateOption = (optionIndex: number, value: string) => {
    const newOptions = [...localOptions];
    newOptions[optionIndex] = value;
    setLocalOptions(newOptions);
    onUpdate({ options: newOptions });
  };

  const handleRemoveOption = (optionIndex: number) => {
    const newOptions = localOptions.filter((_, i) => i !== optionIndex);
    setLocalOptions(newOptions);
    onUpdate({ options: newOptions });
  };

  const handleTypeChange = (newType: string) => {
    const updates: Partial<Question> = { type: newType as Question['type'] };
    
    // Initialize options for multiple choice
    if (newType === 'multiple_choice' && !question.options?.length) {
      updates.options = ['Option 1', 'Option 2'];
      setLocalOptions(['Option 1', 'Option 2']);
    } else if (newType !== 'multiple_choice') {
      updates.options = undefined;
      setLocalOptions([]);
    }
    
    onUpdate(updates);
  };

  return (
    <Card className={clsx(
      'p-6 group relative transition-all duration-300',
      isDragging ? 'shadow-xl rotate-2 scale-105' : 'hover:shadow-lg hover:border-primary-300'
    )}>
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="drag-handle cursor-move opacity-0 group-hover:opacity-100 transition-opacity">
            <GripVertical className="w-5 h-5 text-gray-400" />
          </div>
          <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-2xl flex items-center justify-center text-sm font-bold shadow-lg">
            {index + 1}
          </div>
          <div>
            <div className="font-bold text-gray-900 text-lg">Question {index + 1}</div>
            <div className="text-sm text-gray-600 flex items-center space-x-2">
              <Icon className="w-3 h-3" />
              <span>{currentType?.label}</span>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-3">
          {/* Enable/Disable Toggle */}
          <Switch
            checked={question.enabled !== false}
            onCheckedChange={(checked) => onUpdate({ enabled: checked })}
          />

          <Button
            variant="ghost"
            size="sm"
            onClick={onDelete}
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Question Type Selector */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Question Type
        </label>
        <Select value={question.type} onValueChange={handleTypeChange}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {QUESTION_TYPES.map(type => (
              <SelectItem key={type.value} value={type.value}>
                {type.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Question Text */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Question Text
        </label>
        {isEditing ? (
          <div className="space-y-2">
            <Textarea
              value={localText}
              onChange={(e) => setLocalText(e.target.value)}
              rows={3}
              placeholder="Enter your question..."
            />
            <div className="flex space-x-2">
              <Button size="sm" onClick={handleSaveText}>
                Save
              </Button>
              <Button variant="ghost" size="sm" onClick={handleCancelEdit}>
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <div 
            className="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors group/text"
            onClick={() => setIsEditing(true)}
          >
            <p className="text-gray-900">{question.text}</p>
            <div className="flex items-center mt-2 text-sm text-gray-500 opacity-0 group-hover/text:opacity-100 transition-opacity">
              <Edit3 className="w-3 h-3 mr-1" />
              Click to edit
            </div>
          </div>
        )}
      </div>

      {/* Multiple Choice Options */}
      {question.type === 'multiple_choice' && (
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">
            Options
          </label>
          {localOptions.map((option, optionIndex) => (
            <div key={optionIndex} className="flex items-center space-x-2">
              <Input
                type="text"
                value={option}
                onChange={(e) => handleUpdateOption(optionIndex, e.target.value)}
                className="flex-1"
                placeholder={`Option ${optionIndex + 1}`}
              />
              {localOptions.length > 2 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveOption(optionIndex)}
                  className="text-red-600 hover:text-red-700"
                >
                  <X className="w-4 h-4" />
                </Button>
              )}
            </div>
          ))}
          
          <Button
            variant="ghost"
            size="sm"
            onClick={handleAddOption}
            className="text-primary-600 hover:text-primary-700"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add Option
          </Button>
        </div>
      )}

      {/* Required Toggle */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={question.required !== false}
            onChange={(e) => onUpdate({ required: e.target.checked })}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700">Required question</span>
        </label>
      </div>
    </Card>
  );
};