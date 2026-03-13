'use client'

import React, { useEffect, useState } from 'react';
import { useSessionStore } from '@/stores/sessionStore';
import { useAuthStore } from '@/stores/authStore';
import { SessionList } from './SessionList';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import { DelayedSkeleton } from './DelayedSkeleton';
import { Menu, X, LogOut, Sparkles, MessageSquare, MoreHorizontal, ChevronDown } from 'lucide-react';
import type { ContentBlock } from '@/types/message';

/**
 * ChatInterface Component - Gemini-inspired Clean Design
 * 
 * Based on gemini-chatbot's minimalist approach with:
 * - Clean white background with subtle gray sidebar
 * - Simple typography and spacing
 * - Minimal color palette (black, white, grays)
 * - Clean borders and rounded corners
 * - Focus on content over decoration
 */
export const ChatInterface: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { logout, username } = useAuthStore();
  const {
    currentSessionId,
    messages,
    isLoadingMessages,
    isStreaming,
    streamingMessage,
    fetchSessions,
    createSession,
    sendMessage,
    stopStreaming,
  } = useSessionStore();

  // Fetch sessions on mount
  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handleSendMessage = async (content: ContentBlock[]) => {
    await sendMessage(content);
  };

  const handleStopStreaming = () => {
    stopStreaming();
  };

  const handleLogout = () => {
    logout();
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex h-screen bg-white font-sans text-slate-900">
      {/* Sidebar - Clean Design */}
      <aside
        className={`
          fixed md:relative inset-y-0 left-0 z-50
          w-64 bg-[#f5f5f5] border-r border-slate-200
          transform transition-transform duration-200
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0
          flex flex-col
          shadow-lg md:shadow-none
        `}
      >
        {/* Sidebar Header */}
        <div className="p-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-black rounded-md flex items-center justify-center text-white">
              <Sparkles size={14} />
            </div>
            <span className="font-bold text-lg tracking-tight">AI Assistant</span>
            <ChevronDown size={14} className="text-slate-400" />
          </div>
          
          <button
            onClick={toggleSidebar}
            className="md:hidden p-2 hover:bg-slate-200/50 rounded-lg transition-colors"
            aria-label="Close sidebar"
          >
            <X className="w-4 h-4 text-slate-600" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-slate-900 bg-white rounded-lg shadow-sm">
            <MessageSquare size={18} />
            Chat
          </button>

          <div className="pt-8 pb-2">
            <span className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Recent Sessions</span>
          </div>
          <div className="space-y-1">
            <SessionList />
          </div>
        </nav>

        {/* User Section */}
        <div className="p-4 border-t border-slate-200">
          <div className="flex items-center gap-3 px-2">
            <div className="w-8 h-8 rounded-full bg-slate-300 flex items-center justify-center text-sm font-semibold text-slate-700">
              {username?.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-900 truncate">{username}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-1 hover:bg-slate-200/50 rounded transition-colors"
              aria-label="Logout"
            >
              <LogOut size={16} className="text-slate-400" />
            </button>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-40 md:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 bg-white">
        {/* Mobile Header */}
        <header className="md:hidden flex items-center px-4 py-3 border-b border-slate-200">
          <button
            onClick={toggleSidebar}
            className="p-2 -ml-2 hover:bg-slate-100 rounded-lg transition-colors"
            aria-label="Open sidebar"
          >
            <Menu className="w-5 h-5 text-slate-600" />
          </button>
          <h1 className="ml-2 text-lg font-bold">AI Assistant</h1>
        </header>

        {/* Chat Content */}
        {currentSessionId ? (
          <>
            <DelayedSkeleton
              type="message"
              count={3}
              isLoading={isLoadingMessages}
              delay={300}
            >
              <MessageList
                messages={messages}
                streamingMessage={streamingMessage}
                isStreaming={isStreaming}
              />
            </DelayedSkeleton>

            <InputArea
              onSendMessage={handleSendMessage}
              isStreaming={isStreaming}
              onStopStreaming={handleStopStreaming}
            />
          </>
        ) : (
          <div className="flex-1 overflow-y-auto custom-scrollbar">
            <div className="max-w-4xl mx-auto px-8 py-12">
              <div className="space-y-12">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Start a conversation</h3>
                
                <div className="text-center py-20 border-2 border-dashed border-slate-100 rounded-3xl">
                  <div className="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-300 mx-auto mb-4">
                    <MessageSquare size={24} />
                  </div>
                  <p className="text-slate-400 text-sm">No messages yet. Start a conversation below.</p>
                </div>
              </div>
            </div>
            
            {/* Input Area for empty state */}
            <div className="p-8 border-t border-slate-200">
              <div className="max-w-4xl mx-auto relative flex items-center gap-4">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    placeholder="Ask AI Assistant anything..."
                    className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-black/5 focus:border-black transition-all text-sm"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        createSession();
                      }
                    }}
                  />
                  <button
                    onClick={createSession}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-slate-400 hover:text-black transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};