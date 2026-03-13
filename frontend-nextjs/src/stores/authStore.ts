import { create } from 'zustand';
import { authService } from '@/services/authService';

interface AuthState {
  token: string | null;
  userId: string | null;
  username: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  register: (username: string, password: string) => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  initializeAuth: () => void;
}

const TOKEN_KEY = 'auth_token';
const USER_ID_KEY = 'user_id';
const USERNAME_KEY = 'username';

/**
 * Zustand store for authentication state management
 * Handles token storage in localStorage and automatic token inclusion in API requests
 */
export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  userId: null,
  username: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  /**
   * Register a new user account
   */
  register: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await authService.register(username, password);
      
      // Store token and user info in localStorage
      localStorage.setItem(TOKEN_KEY, response.access_token);
      localStorage.setItem(USER_ID_KEY, response.user_id);
      localStorage.setItem(USERNAME_KEY, username);
      
      set({
        token: response.access_token,
        userId: response.user_id,
        username: username,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Registration failed',
      });
      throw error;
    }
  },

  /**
   * Login with existing credentials
   */
  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await authService.login(username, password);
      
      // Store token and user info in localStorage
      localStorage.setItem(TOKEN_KEY, response.access_token);
      localStorage.setItem(USER_ID_KEY, response.user_id);
      localStorage.setItem(USERNAME_KEY, response.username);
      
      set({
        token: response.access_token,
        userId: response.user_id,
        username: response.username,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed',
      });
      throw error;
    }
  },

  /**
   * Logout and clear authentication state
   */
  logout: () => {
    // Clear localStorage
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_ID_KEY);
    localStorage.removeItem(USERNAME_KEY);
    
    set({
      token: null,
      userId: null,
      username: null,
      isAuthenticated: false,
      error: null,
    });
  },

  /**
   * Clear error message
   */
  clearError: () => {
    set({ error: null });
  },

  /**
   * Initialize auth state from localStorage on app startup
   */
  initializeAuth: () => {
    const token = localStorage.getItem(TOKEN_KEY);
    const userId = localStorage.getItem(USER_ID_KEY);
    const username = localStorage.getItem(USERNAME_KEY);
    
    if (token && userId && username) {
      set({
        token,
        userId,
        username,
        isAuthenticated: true,
      });
    }
  },
}));

/**
 * Helper function to get the current auth token
 * Used by other services to include token in API requests
 */
export const getAuthToken = (): string | null => {
  return useAuthStore.getState().token;
};

/**
 * Helper function to check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  return useAuthStore.getState().isAuthenticated;
};