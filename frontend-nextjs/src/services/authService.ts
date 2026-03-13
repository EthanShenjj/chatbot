import type { LoginRequest, LoginResponse, RegisterRequest, RegisterResponse } from '@/types/api';
import { getApiBaseUrl } from '@/config/environment';

/**
 * Authentication service for handling user registration and login
 */
class AuthService {
  /**
   * Register a new user account
   */
  async register(username: string, password: string): Promise<RegisterResponse> {
    const response = await fetch(`${getApiBaseUrl()}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password } as RegisterRequest),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Registration failed');
    }

    return response.json();
  }

  /**
   * Login with existing credentials
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${getApiBaseUrl()}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password } as LoginRequest),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Login failed');
    }

    return response.json();
  }
}

export const authService = new AuthService();