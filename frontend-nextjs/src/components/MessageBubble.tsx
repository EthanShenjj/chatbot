'use client'

import React from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';
import type { MessageBubbleProps } from '@/types/components';
import type { ContentBlock } from '@/types/message';
import { Bot } from 'lucide-react';

/**
 * MessageBubble component - Clean Gemini-inspired Design
 */
export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isStreaming = false }) => {
  const isUser = message.role === 'user';

  const textContent = message.content
    .filter((block): block is Extract<ContentBlock, { type: 'text' }> => block.type === 'text')
    .map(block => block.text)
    .join('\n\n');

  const images = message.content.filter(
    (block): block is Extract<ContentBlock, { type: 'image_url' }> => block.type === 'image_url'
  );
  const files = message.content.filter(
    (block): block is Extract<ContentBlock, { type: 'file' }> => block.type === 'file'
  );
  const audio = message.content.filter(
    (block): block is Extract<ContentBlock, { type: 'audio' }> => block.type === 'audio'
  );

  return (
    <div className="flex gap-6 py-6">
      {/* Avatar */}
      <div className="flex-shrink-0">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center mt-1 ${
          isUser ? 'bg-slate-100' : 'bg-black'
        }`}>
          {isUser ? (
            <div className="w-full h-full rounded-full bg-slate-300 flex items-center justify-center text-xs font-semibold text-slate-700">
              U
            </div>
          ) : (
            <Bot size={16} className="text-white" />
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Role label */}
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-bold">{isUser ? 'You' : 'AI Assistant'}</span>
          <span className="text-[10px] text-slate-400 uppercase tracking-widest">
            {new Date(message.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        {/* Text content */}
        {textContent && (
          <div className="markdown-body text-slate-700">
            <MarkdownRenderer content={textContent} />
            {isStreaming && (
              <span className="inline-block w-2 h-5 ml-1 bg-slate-400 animate-pulse rounded-sm" />
            )}
          </div>
        )}

        {/* Images */}
        {images.length > 0 && (
          <div className="mt-4 space-y-3">
            {images.map((img, idx) => (
              <div key={idx} className="rounded-lg overflow-hidden border border-slate-200">
                <img
                  src={img.image_url.url}
                  alt="Uploaded image"
                  className="max-w-full h-auto"
                  loading="lazy"
                />
              </div>
            ))}
          </div>
        )}

        {/* Files */}
        {files.length > 0 && (
          <div className="mt-4 space-y-2">
            {files.map((file, idx) => (
              <a
                key={idx}
                href={file.file.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 p-3 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
              >
                <div className="w-8 h-8 rounded bg-slate-100 flex items-center justify-center">
                  <svg
                    className="w-4 h-4 text-slate-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <span className="text-sm text-slate-700">{file.file.name}</span>
              </a>
            ))}
          </div>
        )}

        {/* Audio */}
        {audio.length > 0 && (
          <div className="mt-4 space-y-3">
            {audio.map((aud, idx) => (
              <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <audio controls className="w-full max-w-md">
                  <source src={aud.audio.url} />
                  Your browser does not support the audio element.
                </audio>
              </div>
            ))}
          </div>
        )}

        {/* Interrupted indicator */}
        {message.interrupted && (
          <div className="mt-3 inline-flex items-center gap-2 px-2 py-1 bg-amber-50 border border-amber-200 rounded text-xs text-amber-700">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            Response interrupted
          </div>
        )}
      </div>
    </div>
  );
};