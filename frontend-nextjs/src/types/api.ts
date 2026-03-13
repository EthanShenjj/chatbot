import type { Message, ContentBlock, MessageRole } from './message';

/**
 * Authentication API types
 */
export interface RegisterRequest {
  username: string;
  password: string;
}

export interface RegisterResponse {
  access_token: string;
  user_id: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  user_id: string;
  username: string;
}

/**
 * Session API types
 */
export interface SessionsResponse {
  sessions: Array<{
    id: string;
    title: string;
    updated_at: string;
  }>;
}

export interface CreateSessionResponse {
  session_id: string;
  created_at: string;
}

export interface SessionMessagesResponse {
  messages: Message[];
}

/**
 * Chat completion API types
 */
export interface ChatMessage {
  role: MessageRole;
  content: string | ContentBlock[];
}

export interface ChatCompletionRequest {
  session_id: string;
  messages: ChatMessage[];
  stream: boolean;
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface ChatCompletionChunk {
  choices: Array<{
    delta: {
      content?: string;
    };
  }>;
}

/**
 * File upload API types
 */
export interface FileUploadResponse {
  url: string;
  filename: string;
  size: number;
  type: string;
}

export interface FileUploadError {
  error: string;
  code: 'INVALID_FILE_TYPE' | 'FILE_TOO_LARGE';
}

/**
 * Error response type
 */
export interface ApiError {
  error: string;
  code: string;
}