import { create } from 'zustand';
import { Form, Question, FormBuilderState } from '@/types';
import { apiService } from '@/services/api';
import { useAuthStore } from './authStore';

interface FormStore extends FormBuilderState {
  forms: Form[];
  isLoading: boolean;
  error: string | null;

  // Actions
  setCurrentForm: (form: Form | null) => void;
  setIsEditing: (isEditing: boolean, formId?: string) => void;
  setIsDirty: (isDirty: boolean) => void;
  updateCurrentForm: (updates: Partial<Form>) => void;
  updateQuestion: (questionIndex: number, updates: Partial<Question>) => void;
  addQuestion: (question: Question) => void;
  removeQuestion: (questionIndex: number) => void;
  reorderQuestions: (startIndex: number, endIndex: number) => void;

  // API Actions
  inferFormFromText: (textDump: string) => Promise<void>;
  saveForm: (formData: Partial<Form>) => Promise<string>;
  loadForms: () => Promise<void>;
  loadForm: (formId: string) => Promise<void>;

  // Reset
  resetFormBuilder: () => void;
}

export const useFormStore = create<FormStore>((set, get) => ({
  // State
  currentForm: null,
  isEditing: false,
  editingFormId: null,
  isDirty: false,
  forms: [],
  isLoading: false,
  error: null,

  // Basic setters
  setCurrentForm: (form) => set({ currentForm: form }),

  setIsEditing: (isEditing, formId) =>
    set({
      isEditing,
      editingFormId: formId || null,
    }),

  setIsDirty: (isDirty) => set({ isDirty }),

  // Form updates
  updateCurrentForm: (updates) =>
    set((state) => ({
      currentForm: state.currentForm
        ? { ...state.currentForm, ...updates }
        : null,
      isDirty: true,
    })),

  updateQuestion: (questionIndex, updates) =>
    set((state) => {
      if (!state.currentForm) return state;

      const questions = [...state.currentForm.questions];
      questions[questionIndex] = { ...questions[questionIndex], ...updates };

      return {
        currentForm: { ...state.currentForm, questions },
        isDirty: true,
      };
    }),

  addQuestion: (question) =>
    set((state) => {
      if (!state.currentForm) return state;

      return {
        currentForm: {
          ...state.currentForm,
          questions: [...state.currentForm.questions, question],
        },
        isDirty: true,
      };
    }),

  removeQuestion: (questionIndex) =>
    set((state) => {
      if (!state.currentForm) return state;

      const questions = state.currentForm.questions.filter(
        (_, index) => index !== questionIndex
      );

      return {
        currentForm: { ...state.currentForm, questions },
        isDirty: true,
      };
    }),

  reorderQuestions: (startIndex, endIndex) =>
    set((state) => {
      if (!state.currentForm) return state;

      const questions = [...state.currentForm.questions];
      const [reorderedItem] = questions.splice(startIndex, 1);
      questions.splice(endIndex, 0, reorderedItem);

      return {
        currentForm: { ...state.currentForm, questions },
        isDirty: true,
      };
    }),

  // API Actions
  inferFormFromText: async (textDump: string) => {
    const { user } = useAuthStore.getState();

    try {
      set({ isLoading: true, error: null });

      // For development, allow API calls even without auth
      if (!user) throw new Error('User not authenticated');
      const formData = await apiService.inferForm(textDump, user);

      const newForm: Form = {
        form_id: '',
        title: formData.title,
        questions: formData.questions.map((q, index) => ({
          ...q,
          id: `q_${index}`,
          enabled: true,
        })),
        demographics: [],
        created_at: new Date().toISOString(),
        creator_id: user.uid,
      };

      set({
        currentForm: newForm,
        isLoading: false,
        isDirty: true,
      });
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Failed to generate form',
        isLoading: false,
      });
    }
  },

  saveForm: async (formData: Partial<Form>) => {
    const { user } = useAuthStore.getState();

    try {
      set({ isLoading: true, error: null });

      // For development, allow API calls even without auth
      const result = await apiService.saveForm(formData, user!);

      set({
        isLoading: false,
        isDirty: false,
        editingFormId: result.form_id,
      });

      // Refresh forms list
      get().loadForms();

      return result.form_id;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to save form',
        isLoading: false,
      });
      throw error;
    }
  },

  loadForms: async () => {
    const { user } = useAuthStore.getState();

    try {
      set({ isLoading: true, error: null });

      // For development, allow API calls even without auth
      const forms = await apiService.getForms(user!);
      console.log('ahbdakhdb', forms);
      set({ forms, isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load forms',
        isLoading: false,
      });
    }
  },

  loadForm: async (formId: string) => {
    try {
      set({ isLoading: true, error: null });

      const form = await apiService.getForm(formId);

      set({
        currentForm: form,
        isLoading: false,
        isEditing: true,
        editingFormId: formId,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load form',
        isLoading: false,
      });
    }
  },

  resetFormBuilder: () =>
    set({
      currentForm: null,
      isEditing: false,
      editingFormId: null,
      isDirty: false,
      error: null,
    }),
}));
