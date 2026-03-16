'use client'

import React, { useEffect, useState } from 'react';
import { useSessionStore } from '@/stores/sessionStore';
import { useAuthStore } from '@/stores/authStore';
import { SessionList } from './SessionList';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import DelayedSkeleton from './DelayedSkeleton';
import {
  Menu, X, LogOut, Share2, MoreHorizontal,
  Image, Paperclip, Mic, Send, Settings, BookOpen, Code2,
  BookMarked, FileText, Mail, Info, Search,
} from 'lucide-react';
import { ModelSelector } from './ModelSelector';
import { FileUploadZone } from './FileUploadZone';
import type { ContentBlock } from '@/types/message';

const SUGGESTED_PROMPTS = [
  { title: 'Write a Python script', subtitle: 'Code generation', icon: Code2 },
  { title: 'Explain a topic', subtitle: 'Learning & Research', icon: BookMarked },
  { title: 'Summarize text', subtitle: 'Analysis', icon: FileText },
  { title: 'Draft an email', subtitle: 'Communication', icon: Mail },
];

export const ChatInterface: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [starterPrompt, setStarterPrompt] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
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

  useEffect(() => {
    // Only fetch sessions if authenticated
    if (username) {
      fetchSessions();
    }
  }, [fetchSessions, username]);

  const handleSendMessage = async (content: ContentBlock[]) => {
    await sendMessage(content);
  };

  const handleStarterSend = async () => {
    const trimmed = starterPrompt.trim();
    if (!trimmed || isSending) return;
    setIsSending(true);
    try {
      await createSession();
      await handleSendMessage([{ type: 'text', text: trimmed }]);
      setStarterPrompt('');
    } finally {
      setIsSending(false);
    }
  };

  const handleSuggestion = async (title: string) => {
    setIsSending(true);
    try {
      await createSession();
      await handleSendMessage([{ type: 'text', text: title }]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#f6f7f8] font-sans">
      {/* Sidebar */}
      <aside
        className={`
          fixed md:relative inset-y-0 left-0 z-50
          w-[288px] bg-white border-r border-[#e2e8f0]
          transform transition-transform duration-200
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0 flex flex-col
        `}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-4">
          <div className="w-8 h-8 rounded-lg bg-[#137fec] flex items-center justify-center shrink-0">
            <svg width="15" height="12" viewBox="0 0 15 12" fill="none">
              <path d="M1 6h13M7.5 1l6.5 5-6.5 5" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div>
            <p className="text-[14px] font-semibold text-[#0f172a] leading-[17.5px]">AI Studio</p>
            <p className="text-[11px] font-medium text-[#64748b] leading-[16.5px]">Developer Console</p>
          </div>
          <button
            onClick={() => setIsSidebarOpen(false)}
            className="md:hidden ml-auto p-1.5 hover:bg-gray-100 rounded-lg"
          >
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        {/* New Chat */}
        <div className="px-4 pb-4">
          <button
            onClick={createSession}
            className="w-full flex items-center justify-center gap-2 rounded-lg bg-[#137fec] text-white text-[14px] font-semibold py-2.5 shadow-sm hover:bg-[#0f6ed8] transition-colors"
          >
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
              <path d="M7.5 1v13M1 7.5h13" stroke="white" strokeWidth="1.8" strokeLinecap="round"/>
            </svg>
            New Chat
          </button>
        </div>

        {/* Search Bar */}
        <div className="px-4 pb-4">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search history..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-8 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-[#137fec]/20 focus:border-[#137fec] transition-all placeholder:text-slate-400"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X size={14} />
              </button>
            )}
          </div>
        </div>

        {/* Recent sessions */}
        <div className="flex-1 overflow-y-auto px-2">
          <p className="px-3 mb-2 text-[11px] font-bold text-[#94a3b8] tracking-[0.05em] uppercase">
            Recent
          </p>
          <SessionList searchTerm={searchTerm} />
        </div>

        {/* Bottom nav */}
        <div className="border-t border-[#f1f5f9] px-4 py-4 space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-50 text-[14px] font-medium text-[#475569] transition-colors">
            <Settings size={16} className="text-slate-400" />
            Settings
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-50 text-[14px] font-medium text-[#475569] transition-colors">
            <BookOpen size={16} className="text-slate-400" />
            Documentation
          </button>
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer">
            <div className="w-[18px] h-[18px] rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-[10px] font-bold text-white shrink-0">
              {username?.charAt(0).toUpperCase()}
            </div>
            <span className="text-[14px] font-medium text-[#475569] flex-1 truncate">{username}</span>
            <button
              onClick={logout}
              className="p-1 hover:bg-slate-200 rounded transition-colors"
              aria-label="Logout"
            >
              <LogOut size={14} className="text-slate-400" />
            </button>
          </div>
        </div>
      </aside>

      {/* Mobile overlay */}
      {isSidebarOpen && (
        <div className="fixed inset-0 bg-black/20 z-40 md:hidden" onClick={() => setIsSidebarOpen(false)} />
      )}

      {/* Main */}
      <main className="flex-1 flex flex-col min-w-0 bg-white">
        {/* Header */}
        <header className="h-14 border-b border-slate-200 flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="md:hidden p-2 hover:bg-gray-100 rounded-lg"
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>

            <ModelSelector />

            {/* System prompt */}
            <button className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700 transition-colors">
              <Info size={14} />
              System prompt
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button className="flex items-center gap-2 px-4 py-1.5 text-sm font-medium bg-slate-100 hover:bg-slate-200 rounded-full transition-colors">
              <Share2 size={16} />
              Share
            </button>
            <button className="p-2 text-slate-400 hover:text-slate-600 transition-colors">
              <MoreHorizontal size={18} />
            </button>
          </div>
        </header>

        {/* Content */}
        {currentSessionId ? (
          <div className="flex-1 flex flex-col min-h-0">
            <div className="flex-1 overflow-y-auto">
              <div className="max-w-4xl mx-auto px-6 py-10">
                <DelayedSkeleton type="message" count={3} isLoading={isLoadingMessages} delay={300}>
                  <MessageList
                    messages={messages}
                    streamingMessage={streamingMessage}
                    isStreaming={isStreaming}
                  />
                </DelayedSkeleton>
              </div>
            </div>
            <div className="px-6 py-6 border-t border-slate-100 shrink-0">
              <div className="max-w-4xl mx-auto">
                <InputArea
                  onSendMessage={handleSendMessage}
                  isStreaming={isStreaming}
                  onStopStreaming={stopStreaming}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col min-h-0">
            {/* Welcome + suggestions */}
            <div className="flex-1 flex flex-col items-center justify-center overflow-y-auto px-6">
              <div className="max-w-4xl w-full">
                <h2 className="text-[40px] font-bold text-slate-900 mb-12 tracking-tight text-center">
                  How can I help you today?
                </h2>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {SUGGESTED_PROMPTS.map((item) => {
                    const Icon = item.icon;
                    return (
                      <button
                        key={item.title}
                        type="button"
                        onClick={() => handleSuggestion(item.title)}
                        disabled={isSending}
                        className="p-5 border border-slate-200 rounded-xl hover:border-[#137fec] hover:bg-blue-50/30 transition-all text-left group disabled:opacity-60"
                      >
                        <div className="text-[#137fec] mb-4 group-hover:scale-110 transition-transform">
                          <Icon size={20} />
                        </div>
                        <p className="font-semibold text-[15px] text-slate-900 mb-1">{item.title}</p>
                        <p className="text-[12px] text-slate-500">{item.subtitle}</p>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Starter input */}
            <div className="px-6 py-6 shrink-0">
              <div className="max-w-4xl mx-auto">
                <div className="relative bg-white border border-slate-200 rounded-2xl shadow-sm focus-within:border-[#137fec] focus-within:ring-4 focus-within:ring-blue-50 transition-all">
                  <input
                    type="text"
                    value={starterPrompt}
                    onChange={(e) => setStarterPrompt(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleStarterSend();
                      }
                    }}
                    placeholder="Enter a prompt here"
                    className="w-full px-5 py-4 bg-transparent focus:outline-none text-[15px] resize-none"
                  />
                  <div className="flex items-center justify-between px-4 py-3 border-t border-slate-50">
                    <div className="flex items-center gap-1">
                      <FileUploadZone
                        onFilesUploaded={async (files) => {
                          if (!files.length) return;
                          setIsSending(true);
                          try {
                            await createSession();
                            await handleSendMessage(files);
                          } finally {
                            setIsSending(false);
                          }
                        }}
                      >
                        <button
                          type="button"
                          className="p-2 text-slate-400 hover:text-[#137fec] hover:bg-blue-50 rounded-lg transition-all"
                          aria-label="Upload image"
                        >
                          <Image size={18} />
                        </button>
                      </FileUploadZone>
                      <button
                        type="button"
                        className="p-2 text-slate-400 hover:text-[#137fec] hover:bg-blue-50 rounded-lg transition-all"
                        aria-label="Attach file"
                      >
                        <Paperclip size={18} />
                      </button>
                      <button
                        type="button"
                        className="p-2 text-slate-400 hover:text-[#137fec] hover:bg-blue-50 rounded-lg transition-all"
                        aria-label="Voice input"
                      >
                        <Mic size={18} />
                      </button>
                    </div>

                    <button
                      type="button"
                      onClick={handleStarterSend}
                      disabled={!starterPrompt.trim() || isSending}
                      className={`flex items-center gap-2 px-5 py-2 rounded-xl font-medium text-sm transition-all ${
                        !starterPrompt.trim() || isSending
                          ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                          : 'bg-[#137fec] text-white shadow-md shadow-blue-200 hover:bg-[#0f6ed8] active:scale-95'
                      }`}
                    >
                      Send
                      <Send size={16} />
                    </button>
                  </div>
                </div>
                <p className="text-[11px] text-center text-slate-400 mt-4 uppercase tracking-wider font-medium">
                  AI may display inaccurate info, including about people, so double-check its responses.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
