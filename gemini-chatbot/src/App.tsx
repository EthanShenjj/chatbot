/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef, useEffect } from 'react';
import { GoogleGenAI } from "@google/genai";
import { 
  Send, 
  Bot, 
  User, 
  Loader2, 
  Trash2, 
  MessageSquare,
  Sparkles,
  Info,
  Home,
  Calendar,
  ShoppingBag,
  Settings,
  ChevronDown,
  Plus,
  MoreHorizontal
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import ReactMarkdown from 'react-markdown';

// Types
interface Message {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: number;
}

interface ChatHistory {
  id: string;
  title: string;
  date: string;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [history] = useState<ChatHistory[]>([
    { id: '1', title: 'Bear Hug: Live in Concert', date: 'May 9, 2024' },
    { id: '2', title: 'Six Fingers — DJ Set', date: 'May 5, 2024' },
    { id: '3', title: 'We All Look The Same', date: 'Apr 28, 2024' },
    { id: '4', title: 'Viking People', date: 'Apr 23, 2024' },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Initialize Gemini
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || '' });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      text: input.trim(),
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const chatSession = ai.chats.create({
        model: "gemini-3.1-pro-preview",
        config: {
          systemInstruction: "You are a helpful AI assistant. Use markdown for formatting. Keep responses professional and clear.",
        },
        history: messages.map(m => ({
          role: m.role,
          parts: [{ text: m.text }]
        }))
      });

      const result = await chatSession.sendMessageStream({
        message: userMessage.text,
      });

      const botMessageId = (Date.now() + 1).toString();
      let fullText = '';

      setMessages(prev => [...prev, {
        id: botMessageId,
        role: 'model',
        text: '',
        timestamp: Date.now(),
      }]);

      for await (const chunk of result) {
        const chunkText = chunk.text;
        fullText += chunkText;
        setMessages(prev => prev.map(msg => 
          msg.id === botMessageId ? { ...msg, text: fullText } : msg
        ));
      }

    } catch (err: any) {
      console.error("Chat error:", err);
      setError("Failed to get response. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="flex h-screen bg-white font-sans text-slate-900">
      {/* Sidebar */}
      <aside className="w-64 bg-[#f5f5f5] border-r border-slate-200 flex flex-col hidden md:flex">
        <div className="p-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-black rounded-md flex items-center justify-center text-white">
              <Sparkles size={14} />
            </div>
            <span className="font-bold text-lg tracking-tight">Catalyst</span>
            <ChevronDown size={14} className="text-slate-400" />
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-slate-900 bg-white rounded-lg shadow-sm">
            <Home size={18} />
            Home
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-slate-500 hover:bg-slate-200/50 rounded-lg transition-colors">
            <Calendar size={18} />
            Events
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-slate-500 hover:bg-slate-200/50 rounded-lg transition-colors">
            <ShoppingBag size={18} />
            Orders
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-slate-500 hover:bg-slate-200/50 rounded-lg transition-colors">
            <Settings size={18} />
            Settings
          </button>

          <div className="pt-8 pb-2">
            <span className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Upcoming Events</span>
          </div>
          {history.map(item => (
            <button key={item.id} className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-600 hover:text-slate-900 transition-colors text-left">
              {item.title}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-200">
          <div className="flex items-center gap-3 px-2">
            <div className="w-8 h-8 rounded-full bg-slate-300 overflow-hidden">
              <img src="https://picsum.photos/seed/erica/100/100" alt="Avatar" referrerPolicy="no-referrer" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-900 truncate">Erica</p>
            </div>
            <MoreHorizontal size={16} className="text-slate-400" />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 bg-white">
        {/* Header */}
        <header className="h-16 border-b border-slate-200 flex items-center justify-between px-8">
          <h2 className="text-xl font-bold">Good afternoon, Erica</h2>
          <div className="flex items-center gap-4">
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
              Last week
              <ChevronDown size={14} className="text-slate-400" />
            </button>
          </div>
        </header>

        {/* Chat Content */}
        <div className="flex-1 overflow-y-auto custom-scrollbar" ref={chatContainerRef}>
          <div className="max-w-4xl mx-auto px-8 py-12">
            <div className="mb-12">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-6">Overview</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div>
                  <p className="text-sm text-slate-500 mb-1">Total revenue</p>
                  <p className="text-2xl font-bold">$2.6M</p>
                  <div className="flex items-center gap-1 mt-2">
                    <span className="px-1.5 py-0.5 bg-green-100 text-green-700 text-[10px] font-bold rounded">+4.5%</span>
                    <span className="text-[10px] text-slate-400">from last week</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-slate-500 mb-1">Average order value</p>
                  <p className="text-2xl font-bold">$455</p>
                  <div className="flex items-center gap-1 mt-2">
                    <span className="px-1.5 py-0.5 bg-pink-100 text-pink-700 text-[10px] font-bold rounded">-0.5%</span>
                    <span className="text-[10px] text-slate-400">from last week</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-slate-500 mb-1">Tickets sold</p>
                  <p className="text-2xl font-bold">5,888</p>
                  <div className="flex items-center gap-1 mt-2">
                    <span className="px-1.5 py-0.5 bg-green-100 text-green-700 text-[10px] font-bold rounded">+4.5%</span>
                    <span className="text-[10px] text-slate-400">from last week</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-slate-500 mb-1">Total revenue</p>
                  <p className="text-2xl font-bold">$823,067</p>
                  <div className="flex items-center gap-1 mt-2">
                    <span className="px-1.5 py-0.5 bg-green-100 text-green-700 text-[10px] font-bold rounded">+4.5%</span>
                    <span className="text-[10px] text-slate-400">from last week</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-12">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Recent conversation</h3>
              
              {messages.length === 0 ? (
                <div className="text-center py-20 border-2 border-dashed border-slate-100 rounded-3xl">
                  <div className="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-300 mx-auto mb-4">
                    <MessageSquare size={24} />
                  </div>
                  <p className="text-slate-400 text-sm">No messages yet. Start a conversation below.</p>
                </div>
              ) : (
                <div className="space-y-8">
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex gap-6"
                    >
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 ${
                        message.role === 'user' ? 'bg-slate-100' : 'bg-black'
                      }`}>
                        {message.role === 'user' ? (
                          <img src="https://picsum.photos/seed/erica/100/100" alt="User" className="w-full h-full rounded-full" referrerPolicy="no-referrer" />
                        ) : (
                          <Bot size={16} className="text-white" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-bold">{message.role === 'user' ? 'Erica' : 'Catalyst AI'}</span>
                          <span className="text-[10px] text-slate-400 uppercase tracking-widest">
                            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                        <div className="markdown-body text-slate-700">
                          <ReactMarkdown>{message.text}</ReactMarkdown>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}

              {isLoading && (
                <div className="flex gap-6 animate-pulse">
                  <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
                    <Bot size={16} className="text-slate-300" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-slate-50 rounded w-1/4"></div>
                    <div className="h-4 bg-slate-50 rounded w-3/4"></div>
                  </div>
                </div>
              )}
            </div>
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="p-8 border-t border-slate-200">
          <div className="max-w-4xl mx-auto relative flex items-center gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSend();
                }}
                placeholder="Ask Catalyst anything..."
                className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-black/5 focus:border-black transition-all text-sm"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-slate-400 hover:text-black transition-colors"
              >
                <Send size={18} />
              </button>
            </div>
            <button 
              onClick={clearChat}
              className="p-3 border border-slate-200 rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 transition-all"
            >
              <Trash2 size={18} />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
