// Form-related types
export interface Question {
  id: string;
  text: string;
  type: 'text' | 'multiple_choice' | 'yes_no' | 'rating' | 'number';
  options?: string[];
  required?: boolean;
  enabled?: boolean;
}

export interface Form {
  form_id: string;
  title: string;
  questions: Question[];
  demographics: string[];
  created_at: string;
  creator_id: string;
  response_count?: number;
  is_active?: boolean;
}

// Chat-related types  
export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: number;
  session_id: string;
}

export interface ChatSession {
  session_id: string;
  form_id: string;
  messages: ChatMessage[];
  created_at: string;
  device_id?: string;
  location?: {
    city?: string;
    country?: string;
    latitude?: number;
    longitude?: number;
  };
}

// Response-related types
export interface FormResponse {
  response_id: string;
  form_id: string;
  session_id: string;
  responses: Record<string, any>;
  demographics: Record<string, any>;
  transcript: ChatMessage[];
  created_at: string;
  device_id?: string;
  location?: {
    city?: string;
    country?: string;
  };
}

// Import Firebase User type
import { User as FirebaseUser } from 'firebase/auth';

// Use Firebase User type directly
export type User = FirebaseUser;

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface InferResponse {
  title: string;
  questions: Question[];
}

export interface ChatResponse {
  message: string;
  session_id: string;
}

// UI State types
export interface FormBuilderState {
  currentForm: Form | null;
  isEditing: boolean;
  editingFormId: string | null;
  isDirty: boolean;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  sessionId: string | null;
  form: Form | null;
}

// Component Props types
export interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  onClose: () => void;
}

export interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

// Form validation types
export interface ValidationError {
  field: string;
  message: string;
}

export interface FormData {
  title: string;
  textDump: string;
  questions: Question[];
  demographics: string[];
}

// Demographics options
export const DEMOGRAPHIC_OPTIONS = [
  'Age',
  'Gender', 
  'Location',
  'Education',
  'Income',
  'Occupation',
  'Ethnicity'
] as const;

export type DemographicOption = typeof DEMOGRAPHIC_OPTIONS[number];

// Question type options
export const QUESTION_TYPES = [
  { value: 'text', label: 'Text Response', icon: 'type' },
  { value: 'multiple_choice', label: 'Multiple Choice', icon: 'list' },
  { value: 'yes_no', label: 'Yes/No', icon: 'check-circle' },
  { value: 'rating', label: 'Rating (1-5)', icon: 'star' },
  { value: 'number', label: 'Number', icon: 'hash' }
] as const;

export type QuestionType = typeof QUESTION_TYPES[number]['value'];