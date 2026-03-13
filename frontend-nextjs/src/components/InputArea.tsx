'use client'

import React, { useState, useRef, useEffect } from 'react';
import { Send, Square, Paperclip, Trash2 } from 'lucide-react';
import { FileUploadZone } from './FileUploadZone';
import type { ContentBlock } from '@/types/message';

interface InputAreaProps {
  onSendMessage: (content: ContentBlock[]) => Promise<void>;
  isStreaming: boolean;
  onStopStreaming: () => void;
}

/**
 * InputArea Component - Clean Gemini-inspired Design
 */
export const InputArea: React.FC<InputAreaProps> = ({
  onSendMessage,
  isStreaming,
  onStopStreaming,
}) => {
  const [text, setText] = useState('');
  const [attachments, setAttachments] = useState<ContentBlock[]>([]);
  const [isSending, setIsSending] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if ((!text.trim() && attachments.length === 0) || isSending) {
      return;
    }

    const content: ContentBlock[] = [];
    
    if (text.trim()) {
      content.push({ type: 'text', text: text.trim() });
    }
    
    content.push(...attachments);

    setIsSending(true);
    try {
      await onSendMessage(content);
      setText('');
      setAttachments([]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileUpload = (files: ContentBlock[]) => {
    setAttachments(prev => [...prev, ...files]);
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setText('');
    setAttachments([]);
  };
  return (
    <div className="p-8 border-t border-slate-200">
      <div className="max-w-4xl mx-auto">
        {/* Attachments Preview */}
        {attachments.length > 0 && (
          <div className="mb-4 flex flex-wrap gap-2">
            {attachments.map((attachment, index) => (
              <div
                key={index}
                className="relative group bg-slate-50 border border-slate-200 rounded-lg p-2 pr-8"
              >
                <span className="text-sm text-slate-700">
                  {attachment.type === 'image_url' ? '🖼️ Image' : '📎 File'}
                </span>
                <button
                  onClick={() => removeAttachment(index)}
                  className="absolute right-1 top-1 p-1 rounded hover:bg-slate-200 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Input Container */}
        <div className="relative flex items-center gap-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask AI Assistant anything..."
              disabled={isSending || isStreaming}
              className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-black/5 focus:border-black transition-all text-sm"
            />
            
            {/* Send Button */}
            <button
              onClick={handleSubmit}
              disabled={(!text.trim() && attachments.length === 0) || isSending}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-slate-400 hover:text-black transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Send size={18} />
            </button>
          </div>

          {/* File Upload */}
          <FileUploadZone onFilesUploaded={handleFileUpload}>
            <button
              type="button"
              className="p-3 border border-slate-200 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-all"
              aria-label="Attach file"
            >
              <Paperclip size={18} />
            </button>
          </FileUploadZone>

          {/* Stop/Clear Button */}
          {isStreaming ? (
            <button
              onClick={onStopStreaming}
              className="p-3 border border-slate-200 rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 transition-all"
              aria-label="Stop generating"
            >
              <Square size={18} />
            </button>
          ) : (
            <button
              onClick={clearAll}
              className="p-3 border border-slate-200 rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 transition-all"
              aria-label="Clear input"
            >
              <Trash2 size={18} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};