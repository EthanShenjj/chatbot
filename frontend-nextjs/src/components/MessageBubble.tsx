'use client'

import React, { useState } from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';
import type { MessageBubbleProps } from '@/types/components';
import type { ContentBlock } from '@/types/message';
import { Copy, Download, RotateCcw, Check, User, Bot } from 'lucide-react';

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isStreaming = false }) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const textContent = message.content
    .filter((block): block is Extract<ContentBlock, { type: 'text' }> => block.type === 'text')
    .map(b => b.text)
    .join('\n\n');

  const images = message.content.filter(
    (b): b is Extract<ContentBlock, { type: 'image_url' }> => b.type === 'image_url'
  );

  const handleCopy = () => {
    navigator.clipboard.writeText(textContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const downloadMarkdown = () => {
    const blob = new Blob([textContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-response-${message.id}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (isUser) {
    // User message - right aligned
    return (
      <div className="flex justify-end group">
        <div className="flex flex-col items-end gap-2 max-w-[80%]">
          {/* Message bubble */}
          <div className="bg-[#137fec] text-white rounded-2xl rounded-tr-sm px-5 py-3.5 shadow-sm">
            <p className="text-[15px] leading-relaxed whitespace-pre-wrap break-words">{textContent}</p>
            {images.map((img, i) => (
              <img key={i} src={img.image_url.url} alt="" className="mt-2 rounded-lg max-w-full" />
            ))}
          </div>

          {/* Action buttons */}
          {!isStreaming && (
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <ActionBtn onClick={handleCopy} title="Copy">
                {copied ? <Check size={14} className="text-emerald-500" /> : <Copy size={14} />}
              </ActionBtn>
            </div>
          )}
        </div>
      </div>
    );
  }

  // AI message - left aligned
  return (
    <div className="flex justify-start group">
      <div className="flex gap-3 max-w-[80%]">
        {/* Avatar */}
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
            <Bot size={16} className="text-[#137fec]" />
          </div>
        </div>

        {/* Content */}
        <div className="flex flex-col gap-2 flex-1 min-w-0">
          {/* Message bubble */}
          <div className="bg-slate-50 border border-slate-100 text-slate-800 rounded-2xl rounded-tl-sm px-5 py-3.5 shadow-sm">
            <div className="text-[15px] leading-relaxed">
              <MarkdownRenderer content={textContent} isUserMessage={false} />
              {isStreaming && (
                <span className="inline-block w-[3px] h-[1.1em] ml-0.5 bg-slate-400 animate-pulse rounded-sm align-middle" />
              )}
            </div>
            {images.map((img, i) => (
              <img key={i} src={img.image_url.url} alt="" className="mt-3 rounded-xl max-w-full border border-slate-100" />
            ))}
          </div>

          {/* Interrupted badge */}
          {message.interrupted && (
            <span className="inline-block text-[11px] text-amber-600 bg-amber-50 border border-amber-200 rounded px-2 py-0.5 self-start">
              Response interrupted
            </span>
          )}

          {/* Action buttons */}
          {!isStreaming && (
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <ActionBtn onClick={handleCopy} title="Copy">
                {copied ? <Check size={14} className="text-emerald-500" /> : <Copy size={14} />}
              </ActionBtn>
              <ActionBtn onClick={downloadMarkdown} title="Download Markdown">
                <Download size={14} />
              </ActionBtn>
              <ActionBtn title="Regenerate">
                <RotateCcw size={14} />
              </ActionBtn>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const ActionBtn: React.FC<{ onClick?: () => void; title: string; children: React.ReactNode }> = ({
  onClick, title, children,
}) => (
  <button
    onClick={onClick}
    title={title}
    className="p-1.5 rounded-md text-slate-400 hover:text-[#137fec] hover:bg-blue-50 transition-all"
  >
    {children}
  </button>
);
