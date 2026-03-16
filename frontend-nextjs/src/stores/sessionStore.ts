import { create } from 'zustand';
import { sessionService } from '@/services/sessionService';
import { sseClient } from '@/services/sseClient';
import type { Session, Message, ContentBlock } from '@/types/message';

interface SessionState {
  sessions: Session[];
  currentSessionId: string | null;
  messages: Message[];
  isLoadingSessions: boolean;
  isLoadingMessages: boolean;
  isStreaming: boolean;
  streamingMessage: string;
  error: string | null;
  networkError: boolean;
  
  // Actions
  fetchSessions: () => Promise<void>;
  createSession: () => Promise<string>;
  selectSession: (sessionId: string) => Promise<void>;
  fetchMessages: (sessionId: string) => Promise<void>;
  sendMessage: (content: ContentBlock[]) => Promise<void>;
  stopStreaming: () => void;
  clearError: () => void;
  clearCurrentSession: () => void;
  deleteSession: (sessionId: string) => Promise<void>;
}

/**
 * Zustand store for session state management
 * Handles session list, current session, and message history
 */
export const useSessionStore = create<SessionState>((set, get) => ({
  sessions: [],
  currentSessionId: null,
  messages: [],
  isLoadingSessions: false,
  isLoadingMessages: false,
  isStreaming: false,
  streamingMessage: '',
  error: null,
  networkError: false,

  /**
   * Fetch all sessions for the authenticated user
   */
  fetchSessions: async () => {
    set({ isLoadingSessions: true, error: null });

    const timeout = window.setTimeout(() => {
      if (get().isLoadingSessions) {
        set({ isLoadingSessions: false });
      }
    }, 15000);

    try {
      const response = await sessionService.getSessions();
      set({ sessions: response.sessions, isLoadingSessions: false, error: null });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch sessions';
      
      // Don't set error state for auth errors - user will be redirected to login
      if (!errorMessage.includes('Unauthorized')) {
        set({
          isLoadingSessions: false,
          error: errorMessage,
        });
      } else {
        set({ isLoadingSessions: false });
      }
      
      // Don't throw for auth errors to prevent console noise
      if (!errorMessage.includes('Unauthorized')) {
        throw error;
      }
    } finally {
      clearTimeout(timeout);
    }
  },

  /**
   * Create a new session and select it
   * Returns the new session ID
   */
  createSession: async () => {
    set({ error: null });
    
    try {
      const response = await sessionService.createSession();
      
      // Add new session to the list at the top
      const newSession: Session = {
        id: response.session_id,
        title: 'New conversation',
        updated_at: response.created_at,
      };
      
      set((state) => ({
        sessions: [newSession, ...state.sessions],
        currentSessionId: response.session_id,
        messages: [],
        error: null,
      }));
      
      return response.session_id;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create session',
      });
      throw error;
    }
  },

  /**
   * Select a session and load its messages
   */
  selectSession: async (sessionId: string) => {
    set({ currentSessionId: sessionId, error: null });
    
    try {
      await get().fetchMessages(sessionId);
    } catch (error) {
      // Error is already set by fetchMessages
      throw error;
    }
  },

  /**
   * Fetch message history for a specific session
   */
  fetchMessages: async (sessionId: string) => {
    set({ isLoadingMessages: true, error: null });

    // Safety timeout: never stay in loading state more than 15s
    const timeout = window.setTimeout(() => {
      if (get().isLoadingMessages) {
        set({ isLoadingMessages: false, error: 'Request timed out' });
      }
    }, 15000);

    try {
      const response = await sessionService.getSessionMessages(sessionId);
      set({ messages: response.messages, isLoadingMessages: false, error: null });
    } catch (error) {
      set({
        isLoadingMessages: false,
        error: error instanceof Error ? error.message : 'Failed to fetch messages',
      });
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  },

  /**
   * Send a message and stream the AI response
   */
  sendMessage: async (content: ContentBlock[]) => {
    const { currentSessionId, messages } = get();
    
    if (!currentSessionId) {
      set({ error: 'No session selected' });
      return;
    }
    
    // Create user message
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      raw_text: content
        .filter((block) => block.type === 'text')
        .map((block) => (block as { text: string }).text)
        .join(' '),
      created_at: new Date().toISOString(),
      timestamp: Date.now(),
    };
    
    // Add user message to state
    set((state) => ({
      messages: [...state.messages, userMessage],
      isStreaming: true,
      streamingMessage: '',
      error: null,
      networkError: false,
    }));
    
    // Prepare messages for API
    const apiMessages = [...messages, userMessage].map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));
    
    try {
      // Get selected model config id from model store
      const { useModelStore } = await import('@/stores/modelStore');
      const modelConfigId = useModelStore.getState().selectedModelId;

      await sseClient.streamCompletion(
        currentSessionId,
        apiMessages,
        (token: string) => {
          set((state) => ({
            streamingMessage: state.streamingMessage + token,
          }));
        },
        async () => {
          const { streamingMessage } = get();
          
          // Create assistant message
          const assistantMessage: Message = {
            id: `temp-assistant-${Date.now()}`,
            role: 'assistant',
            content: [{ type: 'text', text: streamingMessage }],
            raw_text: streamingMessage,
            created_at: new Date().toISOString(),
            timestamp: Date.now(),
          };
          
          // Add to messages and clear streaming state
          set((state) => ({
            messages: [...state.messages, assistantMessage],
            isStreaming: false,
            streamingMessage: '',
          }));
          
          // Refresh messages from server to get persisted IDs
          try {
            await get().fetchMessages(currentSessionId);
          } catch (error) {
            console.error('Failed to refresh messages:', error);
          }
        },
        // onError: handle network errors
        (error: Error) => {
          console.error('Streaming error:', error);
          set({
            isStreaming: false,
            streamingMessage: '',
            networkError: true,
            error: error.message,
          });
        },
        modelConfigId,
      );
    } catch (error) {
      set({
        isStreaming: false,
        streamingMessage: '',
        error: error instanceof Error ? error.message : 'Failed to send message',
      });
    }
  },

  /**
   * Stop the current streaming response
   */
  stopStreaming: () => {
    sseClient.abort();
    
    const { streamingMessage } = get();
    
    // If there's a partial message, save it as interrupted
    if (streamingMessage) {
      const assistantMessage: Message = {
        id: `temp-interrupted-${Date.now()}`,
        role: 'assistant',
        content: [{ type: 'text', text: streamingMessage }],
        raw_text: streamingMessage,
        created_at: new Date().toISOString(),
        timestamp: Date.now(),
        interrupted: true,
      };
      
      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isStreaming: false,
        streamingMessage: '',
      }));
    } else {
      set({
        isStreaming: false,
        streamingMessage: '',
      });
    }
  },

  /**
   * Clear error message
   */
  clearError: () => {
    set({ error: null, networkError: false });
  },

  /**
   * Clear current session selection
   */
  clearCurrentSession: () => {
    set({
      currentSessionId: null,
      messages: [],
    });
  },

  /**
   * Delete a session and remove it from the list
   */
  deleteSession: async (sessionId: string) => {
    await sessionService.deleteSession(sessionId);
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== sessionId),
      currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId,
      messages: state.currentSessionId === sessionId ? [] : state.messages,
    }));
  },
}));

/**
 * Helper function to get the current session ID
 */
export const getCurrentSessionId = (): string | null => {
  return useSessionStore.getState().currentSessionId;
};

/**
 * Helper function to get current messages
 */
export const getCurrentMessages = (): Message[] => {
  return useSessionStore.getState().messages;
};