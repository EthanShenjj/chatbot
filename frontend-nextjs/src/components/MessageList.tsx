'use client'

import React, { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import type { MessageListProps } from '@/types/components';
import type { Message } from '@/types/message';
import { MessageSquare } from 'lucide-react';

/**
 * MessageList Component - Gemini-inspired Clean Style
 */
export const MessageList: React.FC<MessageListProps> = ({
  messages,
  streamingMessage,
  isStreaming,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  const streamingMessageObj: Message | null = streamingMessage
    ? {
        id: 'streaming',
        role: 'assistant',
        content: [{ type: 'text', text: streamingMessage }],
        raw_text: streamingMessage,
        created_at: new Date().toISOString(),
        timestamp: Date.now(),
      }
    : null;

  const allMessages = streamingMessageObj
    ? [...messages, streamingMessageObj]
    : messages;

  if (allMessages.length === 0) {
    return (
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="max-w-4xl mx-auto px-8 py-12">
          <div className="space-y-12">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Recent conversation</h3>
            
            <div className="text-center py-20 border-2 border-dashed border-slate-100 rounded-3xl">
              <div className="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-300 mx-auto mb-4">
                <MessageSquare size={24} />
              </div>
              <p className="text-slate-400 text-sm">No messages yet. Start a conversation below.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar" data-testid="message-list">
      <div className="max-w-4xl mx-auto px-8 py-12">
        <div className="space-y-12">
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Recent conversation</h3>
          
          <div className="space-y-8">
            {allMessages.map((message, index) => (
              <MessageBubble
                key={message.id}
                message={message}
                isStreaming={isStreaming && index === allMessages.length - 1}
              />
            ))}
          </div>
        </div>
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
/**
 * MessageListSkeleton Component
 */
export const MessageListSkeleton: React.FC<{ count?: number }> = ({ count = 3 }) => {
  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar" data-testid="message-list-skeleton">
      <div className="max-w-4xl mx-auto px-8 py-12">
        <div className="space-y-8">
          {Array.from({ length: count }).map((_, idx) => (
            <div key={idx} className="flex gap-6 animate-pulse">
              {/* Avatar skeleton */}
              <div className="w-8 h-8 rounded-full bg-slate-100 flex-shrink-0" />
              
              {/* Content skeleton */}
              <div className="flex-1 space-y-3">
                <div className="h-4 bg-slate-100 rounded w-20" />
                <div className="space-y-2">
                  <div className="h-4 bg-slate-100 rounded w-full" />
                  <div className="h-4 bg-slate-100 rounded w-5/6" />
                  <div className="h-4 bg-slate-100 rounded w-4/6" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};