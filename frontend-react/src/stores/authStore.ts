import { create } from 'zustand';
import { 
  signInWithPopup, 
  GoogleAuthProvider, 
  signOut as firebaseSignOut,
  onAuthStateChanged,
  User
} from 'firebase/auth';
import { auth } from '@/services/firebase';
import { AuthState } from '@/types';

interface AuthStore extends AuthState {
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  initialize: () => void;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  isLoading: true,
  error: null,

  signInWithGoogle: async () => {
    try {
      set({ isLoading: true, error: null });
      
      const provider = new GoogleAuthProvider();
      provider.addScope('email');
      provider.addScope('profile');
      
      const result = await signInWithPopup(auth, provider);
      
      // User will be set by onAuthStateChanged listener
      set({ isLoading: false });
    } catch (error) {
      console.error('Sign in error:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to sign in',
        isLoading: false 
      });
    }
  },

  signOut: async () => {
    try {
      set({ isLoading: true, error: null });
      await firebaseSignOut(auth);
      set({ user: null, isLoading: false });
    } catch (error) {
      console.error('Sign out error:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to sign out',
        isLoading: false 
      });
    }
  },

  initialize: () => {
    const unsubscribe = onAuthStateChanged(auth, (user: User | null) => {
      set({ 
        user: user, // Store the full Firebase user object
        isLoading: false,
        error: null
      });
    });

    // Return unsubscribe function for cleanup
    return unsubscribe;
  }
}));