/**
 * Content block types for multimodal messages
 */
export type ContentBlockType = 'text' | 'image_url' | 'file' | 'audio';

/**
 * Base content block interface
 */
interface BaseContentBlock {
  type: ContentBlockType;
}

/**
 * Text content block
 */
export interface TextContentBlock extends BaseContentBlock {
  type: 'text';
  text: string;
}

/**
 * Image URL content block
 */
export interface ImageUrlContentBlock extends BaseContentBlock {
  type: 'image_url';
  image_url: {
    url: string;
  };
}

/**
 * File content block
 */
export interface FileContentBlock extends BaseContentBlock {
  type: 'file';
  file: {
    url: string;
    name: string;
  };
}

/**
 * Audio content block
 */
export interface AudioContentBlock extends BaseContentBlock {
  type: 'audio';
  audio: {
    url: string;
  };
}

/**
 * Union type for all content blocks
 */
export type ContentBlock =
  | TextContentBlock
  | ImageUrlContentBlock
  | FileContentBlock
  | AudioContentBlock;

/**
 * Message role types
 */
export type MessageRole = 'user' | 'assistant' | 'system';

/**
 * Message interface
 */
export interface Message {
  id: string;
  role: MessageRole;
  content: ContentBlock[];
  raw_text: string;
  created_at: string;
  timestamp?: number;
  interrupted?: boolean;
}

/**
 * Session interface
 */
export interface Session {
  id: string;
  title: string;
  updated_at: string;
}