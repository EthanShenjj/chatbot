'use client'

import React, { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import type { MessageListProps } from '@/types/components';
import type { Message } from '@/types/message';
import { MessageSquare } from 'lucide-react';

/**
 * MessageList Component - Google AI Studio Design
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
    return null;
  }

  return (
    <div className="space-y-6">
      {allMessages.map((message, index) => (
        <MessageBubble
          key={message.id}
          message={message}
          isStreaming={isStreaming && index === allMessages.length - 1}
        />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};
/**
 * MessageListSkeleton Component
 */
export const MessageListSkeleton: React.FC<{ count?: number }> = ({ count = 3 }) => {
  return (
    <div className="space-y-6 animate-pulse">
      {Array.from({ length: count }).map((_, idx) => (
        <div key={idx} className={`flex ${idx % 2 === 0 ? 'justify-start' : 'justify-end'}`}>
          {idx % 2 === 0 ? (
            // AI message skeleton
            <div className="flex gap-3 max-w-[80%]">
              <div className="w-8 h-8 rounded-full bg-slate-200 flex-shrink-0" />
              <div className="flex-1 bg-slate-100 rounded-2xl rounded-tl-sm p-5 space-y-2">
                <div className="h-4 bg-slate-200 rounded w-full" />
                <div className="h-4 bg-slate-200 rounded w-5/6" />
                <div className="h-4 bg-slate-200 rounded w-4/6" />
              </div>
            </div>
          ) : (
            // User message skeleton
            <div className="max-w-[80%]">
              <div className="bg-slate-200 rounded-2xl rounded-tr-sm p-5 space-y-2">
                <div className="h-4 bg-slate-300 rounded w-full" />
                <div className="h-4 bg-slate-300 rounded w-3/4" />
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};