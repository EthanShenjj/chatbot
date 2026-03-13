# Implementation Plan: Minimalist Multimodal AI Assistant

## Overview

This implementation plan breaks down the development of a full-stack AI chat assistant into discrete coding tasks. The system uses Flask + MySQL for the backend, React + TypeScript for the frontend, and implements real-time SSE streaming for AI responses. Tasks are organized to build incrementally, with early validation through testing and checkpoints.

## Tasks

- [x] 1. Set up project structure and database schema
  - Create backend directory structure (Flask app, models, services, routes)
  - Create frontend directory structure (React + Vite + TypeScript)
  - Set up MySQL database and create tables for users, sessions, and messages
  - Configure SQLAlchemy models with JSON column support
  - Set up Alembic for database migrations
  - Create .env.example files for configuration
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 2. Implement authentication system
  - [x] 2.1 Create User model and authentication service
    - Implement User SQLAlchemy model with password hashing
    - Create AuthService with bcrypt password hashing (cost factor 12)
    - Implement JWT token generation with 24-hour expiration
    - Implement JWT token validation
    - _Requirements: 1.1, 1.2_
  
  - [x] 2.2 Write unit tests for authentication service
    - Test password hashing and verification
    - Test JWT token generation and validation
    - Test token expiration handling
    - _Requirements: 1.1, 1.2_
  
  - [x] 2.3 Create authentication API endpoints
    - Implement POST /api/auth/register endpoint
    - Implement POST /api/auth/login endpoint
    - Add JWT authentication middleware for protected routes
    - _Requirements: 1.1, 1.2, 16.4, 16.5_

- [x] 3. Implement session management
  - [x] 3.1 Create Session model and service
    - Implement Session SQLAlchemy model with foreign key to User
    - Create SessionService for CRUD operations
    - Implement session ownership validation
    - _Requirements: 1.3, 1.4, 14.3_
  
  - [x] 3.2 Create session API endpoints
    - Implement GET /api/sessions endpoint (ordered by updated_at DESC)
    - Implement POST /api/sessions endpoint
    - Implement GET /api/sessions/{session_id}/messages endpoint
    - Add session ownership validation middleware
    - _Requirements: 1.5, 12.3, 12.5_

- [x] 4. Implement message content structure and parser
  - [x] 4.1 Create message content parser and validator
    - Implement MessageParser class with content validation
    - Implement content block type validation (text, image_url, file, audio)
    - Implement raw_text extraction from content blocks
    - Implement pretty printer for debugging
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 20.1, 20.2, 20.3, 20.5_
  
  - [ ]* 4.2 Write property test for message parser
    - **Property 1: Round-trip consistency**
    - **Validates: Requirements 20.4**
    - Test that parsing then pretty printing then parsing produces equivalent object
  
  - [x] 4.3 Create Message model
    - Implement Message SQLAlchemy model with JSON content column
    - Add foreign key constraint to Session
    - Add millisecond precision timestamp
    - Add interrupted flag field
    - _Requirements: 14.1, 14.2, 14.5_

- [x] 5. Implement file upload service
  - [x] 5.1 Create file storage service
    - Implement FileStorageService with file validation
    - Implement file type validation (image/png, image/jpeg, image/gif, application/pdf, audio/mpeg, audio/wav)
    - Implement file size validation (10MB limit)
    - Implement unique filename generation using UUID
    - Implement file storage to local filesystem
    - _Requirements: 3.1, 3.2, 3.3, 3.5_
  
  - [x] 5.2 Write unit tests for file storage service
    - Test file type validation
    - Test file size validation
    - Test unique filename generation
    - Test error handling for invalid files
    - _Requirements: 3.1, 3.2, 3.4_
  
  - [x] 5.3 Create file upload API endpoint
    - Implement POST /api/upload endpoint with multipart support
    - Return public URL within 2 seconds
    - Return structured error responses for validation failures
    - _Requirements: 3.3, 3.4_

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement context management service
  - [x] 7.1 Create context manager for token counting and truncation
    - Implement ContextManager class with token calculation
    - Implement context truncation when exceeding 80% of limit
    - Preserve most recent 10 messages during truncation
    - Always include system prompt regardless of truncation
    - Add logging for truncation events
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 7.2 Write unit tests for context manager
    - Test token counting accuracy
    - Test truncation logic
    - Test system prompt preservation
    - Test recent message preservation
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 8. Implement SSE streaming service
  - [x] 8.1 Create stream service for LLM integration
    - Implement StreamService with SSE connection management
    - Implement LLM provider client (requests library)
    - Implement token forwarding from LLM to client
    - Implement stream interruption handling with AbortController pattern
    - Implement response accumulation for database persistence
    - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.2_
  
  - [x] 8.2 Create chat completion API endpoint
    - Implement POST /api/chat/completions endpoint
    - Establish SSE connection with content-type "text/event-stream"
    - Persist user message before streaming
    - Forward tokens through SSE stream
    - Send "data: [DONE]" event on completion
    - Persist complete assistant response after streaming
    - Mark interrupted messages with interrupted flag
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.3, 5.4, 12.1, 12.2, 12.4, 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [ ]* 8.3 Write integration tests for streaming
    - Test SSE connection establishment
    - Test token streaming
    - Test stream completion
    - Test stream interruption
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3_

- [x] 9. Implement error handling and CORS configuration
  - [x] 9.1 Add error handling middleware
    - Implement structured error responses with error codes
    - Implement 503 error with retry-after header for LLM connection failures
    - Implement 401 error for authentication failures
    - Add error logging with timestamp and context
    - _Requirements: 13.1, 13.2, 13.3, 13.5_
  
  - [x] 9.2 Configure CORS and security headers
    - Configure Flask-CORS with allowed origins
    - Add security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
    - Implement origin validation
    - _Requirements: 16.1, 16.2, 16.3_
  
  - [x] 9.3 Add configuration management
    - Load configuration from environment variables
    - Validate required configuration at startup
    - Refuse to start if required config is missing
    - Support configuration of model parameters (temperature, max_tokens, top_p)
    - _Requirements: 19.1, 19.2, 19.3, 19.4_

- [x] 10. Checkpoint - Backend complete, ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Set up frontend project structure
  - [x] 11.1 Initialize React + Vite + TypeScript project
    - Create Vite project with React and TypeScript
    - Install dependencies (shadcn/ui, Tailwind CSS, Zustand, react-markdown, Prism.js, KaTeX)
    - Configure Tailwind CSS with minimalist color palette
    - Set up shadcn/ui component library
    - Create directory structure (components, services, stores, types)
    - _Requirements: 9.1, 9.3_
  
  - [x] 11.2 Create TypeScript interfaces and types
    - Define Message, ContentBlock, Session interfaces
    - Define API request/response types
    - Define component prop types
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 15.1, 15.2_

- [x] 12. Implement authentication UI
  - [x] 12.1 Create authentication service and state management
    - Implement auth API client functions (register, login)
    - Create Zustand auth store with token management
    - Implement token storage in localStorage
    - Implement automatic token inclusion in API requests
    - _Requirements: 1.1, 1.2_
  
  - [x] 12.2 Create login and register components
    - Create LoginForm component with validation
    - Create RegisterForm component with validation
    - Add error display for authentication failures
    - _Requirements: 1.1, 1.2, 13.3_

- [x] 13. Implement session list UI
  - [x] 13.1 Create session service and state management
    - Implement session API client functions (list, create, get messages)
    - Create Zustand session store
    - Implement session selection and creation logic
    - _Requirements: 1.3, 1.4, 1.5_
  
  - [x] 13.2 Create SessionList component
    - Display sessions ordered by most recent activity
    - Show session titles (first 50 chars of first message)
    - Implement session selection with highlight (subtle left border)
    - Implement new session button
    - Add skeleton loaders for loading state
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 18.1, 18.4_

- [-] 14. Implement message display UI
  - [x] 14.1 Create MarkdownRenderer component
    - Integrate react-markdown for markdown conversion
    - Integrate Prism.js for syntax highlighting
    - Integrate KaTeX for LaTeX math rendering
    - Implement HTML sanitization to prevent XSS
    - Render inline images from URLs
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 14.2 Create MessageBubble component
    - Render message content with markdown support
    - Display multimodal content (images, files, audio)
    - Apply minimalist styling (no background boxes, subtle borders)
    - Show interrupted status indicator
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 9.2_
  
  - [x] 14.3 Create MessageList component
    - Display message history with auto-scroll
    - Show streaming message with pulsing cursor
    - Add skeleton loaders for loading state
    - Implement smooth scroll to bottom on new messages
    - _Requirements: 12.3, 18.2, 18.3, 18.4_

- [x] 15. Implement message input UI
  - [x] 15.1 Create FileUploadZone component
    - Implement drag-and-drop event handlers
    - Show visual drop zone indicator on drag over
    - Validate file types and sizes client-side
    - Upload files to backend API
    - Display preview thumbnails
    - Show error messages for upload failures
    - Support multiple file drops
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [x] 15.2 Create InputArea component
    - Implement auto-expanding textarea (max 300px height)
    - Enable vertical scrolling when exceeding max height
    - Reset height after message submission
    - Maintain focus after height adjustments
    - Integrate FileUploadZone for drag-and-drop
    - Display file preview thumbnails
    - Implement send button with loading state
    - Implement stop button for stream interruption
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 16. Implement SSE streaming client
  - [x] 16.1 Create SSE client service
    - Implement SSEClient class with fetch API
    - Implement AbortController for stream interruption
    - Parse SSE data events and extract tokens
    - Handle [DONE] event for stream completion
    - Implement error handling for network failures
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2_
  
  - [x] 16.2 Integrate streaming into message state management
    - Add streaming state to Zustand store
    - Implement token accumulation for display
    - Implement stream interruption action
    - Persist messages after stream completion
    - Show reconnection prompt on network errors
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 13.4_

- [x] 17. Implement main chat interface
  - [x] 17.1 Create ChatInterface component
    - Implement responsive layout with sidebar and chat area
    - Handle mobile breakpoint (768px) with hamburger menu
    - Coordinate session switching and message loading
    - Integrate SessionList, MessageList, and InputArea components
    - _Requirements: 8.1, 8.2, 8.3, 17.1, 17.2_
  
  - [x] 17.2 Apply minimalist styling
    - Use color palette (white #FFFFFF, primary text #111827, secondary text #6B7280)
    - Apply sans-serif fonts (Inter or system UI)
    - Add transition animations (max 200ms duration)
    - Apply whitespace margins (24px between sections)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 18. Implement responsive design
  - [x] 18.1 Add mobile responsive styles
    - Hide sidebar by default on mobile (<768px)
    - Add hamburger menu for sidebar toggle
    - Adjust message bubble max width to 90% on mobile
    - Ensure input field works on screens as small as 320px
    - Maintain minimum 14px font sizes
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

- [x] 19. Implement loading states and skeleton screens
  - [x] 19.1 Create SkeletonLoader component
    - Create skeleton for session list items
    - Create skeleton for message bubbles
    - Add pulsing animation effect
    - _Requirements: 18.1, 18.2, 18.4_
  
  - [x] 19.2 Add loading states throughout UI
    - Show skeletons only for operations >300ms
    - Remove skeletons within 100ms of content availability
    - Show pulsing cursor during streaming
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_

- [x] 20. Configure frontend environment and API integration
  - [x] 20.1 Set up environment configuration
    - Create .env.example with backend API endpoint
    - Load API endpoint from environment variables
    - Configure API client with base URL and auth headers
    - _Requirements: 19.5_
  
  - [x] 20.2 Wire frontend to backend API
    - Connect all API client functions to backend endpoints
    - Test authentication flow end-to-end
    - Test session management end-to-end
    - Test message sending and streaming end-to-end
    - Test file upload end-to-end
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5_

- [-] 21. Final checkpoint - Full integration testing
  - Ensure all tests pass, ask the user if questions arise.
  - Test complete user flow: register → login → create session → send message → receive streaming response
  - Test file upload and multimodal message display
  - Test stream interruption
  - Test session switching and message history loading
  - Test responsive design on different screen sizes
  - Test error handling scenarios

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Backend tasks (1-10) can be developed independently from frontend tasks (11-20)
- Integration testing (20-21) requires both backend and frontend to be complete
