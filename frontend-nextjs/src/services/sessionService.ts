import { get, post } from './apiClient';
import type { SessionsResponse, CreateSessionResponse, SessionMessagesResponse } from '@/types/api';

/**
 * Session service for handling session management
 */
class SessionService {
  /**
   * Get all sessions for the authenticated user
   * Returns sessions ordered by most recent update time
   */
  async getSessions(): Promise<SessionsResponse> {
    const response = await get('/api/sessions');

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch sessions');
    }

    return response.json();
  }

  /**
   * Create a new session
   */
  async createSession(): Promise<CreateSessionResponse> {
    const response = await post('/api/sessions');

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create session');
    }

    return response.json();
  }

  /**
   * Get message history for a specific session
   */
  async getSessionMessages(sessionId: string): Promise<SessionMessagesResponse> {
    const response = await get(`/api/sessions/${sessionId}/messages`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch messages');
    }

    return response.json();
  }
}

export const sessionService = new SessionService();