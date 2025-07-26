import { User } from 'firebase/auth';
import {
  ApiResponse,
  InferResponse,
  ChatResponse,
  Form,
  FormResponse,
} from '@/types';

const isDev = false;

// Always use local API in development
const API_BASE_URL = isDev
  ? 'http://127.0.0.1:5000/api'
  : 'https://us-central1-bermuda-01.cloudfunctions.net/api';

class ApiService {
  private async getAuthHeaders(
    user: User | null
  ): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Only add auth headers if user exists and has getIdToken method
    if (user && typeof user.getIdToken === 'function') {
      try {
        const token = await user.getIdToken();
        headers['Authorization'] = `Bearer ${token}`;
      } catch (error) {
        console.warn('Failed to get ID token:', error);
      }
    }

    return headers;
  }

  async inferForm(textDump: string, user: User): Promise<InferResponse> {
    const headers = await this.getAuthHeaders(user);

    console.log('Making API call to:', `${API_BASE_URL}/infer`);
    console.log('Headers:', headers);

    const response = await fetch(`${API_BASE_URL}/infer`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ dump: textDump }),
    });

    console.log('Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error:', errorText);
      throw new Error('Failed to generate form');
    }

    const data = await response.json();
    console.log('API Response:', data);
    return data;
  }

  async saveForm(
    formData: Partial<Form>,
    user: User
  ): Promise<{ form_id: string }> {
    const headers = await this.getAuthHeaders(user);

    const response = await fetch(`${API_BASE_URL}/save-form`, {
      method: 'POST',
      headers,
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      throw new Error('Failed to save form');
    }

    return response.json();
  }

  async getForms(user: User): Promise<Form[]> {
    const headers = await this.getAuthHeaders(user);

    const response = await fetch(`${API_BASE_URL}/forms`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error('Failed to fetch forms');
    }

    const data = await response.json();
    return data || [];
  }

  async getForm(formId: string): Promise<Form> {
    const response = await fetch(`${API_BASE_URL}/forms/${formId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch form');
    }

    return response.json();
  }

  async getFormResponses(formId: string, user: User): Promise<FormResponse[]> {
    const headers = await this.getAuthHeaders(user);

    const response = await fetch(`${API_BASE_URL}/forms/${formId}/responses`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error('Failed to fetch responses');
    }

    const data = await response.json();
    return data || [];
  }

  async sendChatMessage(
    message: string,
    sessionId: string,
    formId: string
  ): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat-message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        form_id: formId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  }

  async extractFormData(
    sessionId: string,
    formId: string
  ): Promise<FormResponse> {
    const response = await fetch(`${API_BASE_URL}/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        form_id: formId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to extract form data');
    }

    return response.json();
  }
}

export const apiService = new ApiService();
