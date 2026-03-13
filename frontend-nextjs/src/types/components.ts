import type { Message, Session, ContentBlock } from './message';

/**
 * ChatInterface component props
 */
export interface ChatInterfaceProps {
  userId: string;
}

export interface ChatInterfaceState {
  currentSessionId: string | null;
  isSidebarOpen: boolean;
  isLoading: boolean;
}

/**
 * SessionList component props
 */
export interface SessionListProps {
  sessions: Session[];
  currentSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
  onNewSession: () => void;
}

/**
 * MessageList component props
 */
export interface MessageListProps {
  messages: Message[];
  streamingMessage: string | null;
  isStreaming: boolean;
}

/**
 * MessageBubble component props
 */
export interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
}

/**
 * InputArea component props
 */
export interface InputAreaProps {
  onSendMessage: (content: ContentBlock[]) => void;
  isStreaming: boolean;
  onStopStreaming: () => void;
}

export interface InputAreaState {
  text: string;
  attachedFiles: FileAttachment[];
  height: number;
}

/**
 * File attachment type
 */
export interface FileAttachment {
  id: string;
  url: string;
  name: string;
  type: string;
  preview?: string;
}

/**
 * MarkdownRenderer component props
 */
export interface MarkdownRendererProps {
  content: string;
  className?: string;
}

/**
 * FileUploadZone component props
 */
export interface FileUploadZoneProps {
  onFilesUploaded: (files: FileAttachment[]) => void;
  maxFileSize: number;
  allowedTypes: string[];
}

/**
 * SkeletonLoader component props
 */
export interface SkeletonLoaderProps {
  type: 'session' | 'message';
  count?: number;
}