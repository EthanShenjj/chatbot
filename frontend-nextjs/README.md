# AI Assistant - Next.js Frontend

A minimalist multimodal AI assistant built with Next.js, featuring a clean Gemini-inspired design.

## Features

- **Clean Design**: Minimalist interface inspired by gemini-chatbot
- **Multimodal Support**: Text, images, files, and audio
- **Real-time Streaming**: Server-sent events for live responses
- **Session Management**: Persistent conversation history
- **Authentication**: User registration and login
- **Responsive**: Mobile-first design with sidebar navigation
- **TypeScript**: Full type safety throughout the application

## Tech Stack

- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Markdown**: react-markdown with syntax highlighting
- **Math**: KaTeX for LaTeX rendering
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API server running

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy environment variables:
   ```bash
   cp .env.example .env.local
   ```

4. Update `.env.local` with your API base URL:
   ```
   NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
   ```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building

Build for production:

```bash
npm run build
npm start
```

## Project Structure

```
src/
├── app/                 # Next.js app directory
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Home page
├── components/         # React components
│   ├── ChatInterface.tsx
│   ├── MessageList.tsx
│   ├── MessageBubble.tsx
│   ├── InputArea.tsx
│   ├── SessionList.tsx
│   └── ...
├── stores/            # Zustand stores
│   ├── authStore.ts
│   └── sessionStore.ts
├── services/          # API services
│   ├── apiClient.ts
│   ├── authService.ts
│   ├── sessionService.ts
│   └── sseClient.ts
├── types/             # TypeScript types
│   ├── api.ts
│   ├── components.ts
│   └── message.ts
└── config/            # Configuration
    └── environment.ts
```

## Design Philosophy

This application follows a minimalist design approach inspired by gemini-chatbot:

- **Clean Typography**: Inter font family with consistent sizing
- **Minimal Color Palette**: Black, white, and grays as primary colors
- **Simple Interactions**: Clear hover states and transitions
- **Content Focus**: Reduced visual noise to emphasize conversations
- **Responsive Layout**: Mobile-first approach with collapsible sidebar

## API Integration

The frontend communicates with a Python FastAPI backend:

- **Authentication**: JWT-based user authentication
- **Sessions**: Conversation management and persistence  
- **Streaming**: Real-time message streaming via SSE
- **File Upload**: Multimodal content support
- **Error Handling**: Comprehensive error states and recovery

## Contributing

1. Follow the existing code style and patterns
2. Use TypeScript for all new code
3. Maintain the minimalist design principles
4. Test components thoroughly
5. Update documentation as needed

## License

This project is licensed under the MIT License.