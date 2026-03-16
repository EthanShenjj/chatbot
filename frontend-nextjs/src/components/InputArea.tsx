'use client'

import React, { useState, useRef, useEffect } from 'react';
import { Square, Paperclip, Image, Mic, Send } from 'lucide-react';
import { FileUploadZone } from './FileUploadZone';
import type { ContentBlock } from '@/types/message';

interface InputAreaProps {
  onSendMessage: (content: ContentBlock[]) => Promise<void>;
  isStreaming: boolean;
  onStopStreaming: () => void;
}

export const InputArea: React.FC<InputAreaProps> = ({ onSendMessage, isStreaming, onStopStreaming }) => {
  const [text, setText] = useState('');
  const [attachments, setAttachments] = useState<ContentBlock[]>([]);
  const [isSending, setIsSending] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [text]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if ((!text.trim() && attachments.length === 0) || isSending || isStreaming) return;

    const content: ContentBlock[] = [];
    if (text.trim()) content.push({ type: 'text', text: text.trim() });
    content.push(...attachments);

    setIsSending(true);
    try {
      await onSendMessage(content);
      setText('');
      setAttachments([]);
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.altKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const canSend = (text.trim().length > 0 || attachments.length > 0) && !isSending && !isStreaming;

  return (
    <div className="w-full">
      {/* Attachment previews */}
      {attachments.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2 px-1">
          {attachments.map((a, i) => (
            <div key={i} className="flex items-center gap-1.5 bg-slate-100 rounded-lg px-3 py-1.5 text-[13px] text-slate-600">
              <span>{a.type === 'image_url' ? '🖼️' : '📎'} {a.type === 'image_url' ? 'Image' : 'File'}</span>
              <button onClick={() => setAttachments(p => p.filter((_, j) => j !== i))} className="text-slate-400 hover:text-slate-600 ml-1">✕</button>
            </div>
          ))}
        </div>
      )}

      {/* Input box */}
      <div className="relative bg-white border border-slate-200 rounded-2xl shadow-sm focus-within:border-[#137fec] focus-within:ring-4 focus-within:ring-blue-50 transition-all">
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter a prompt here"
          disabled={isSending}
          rows={1}
          className="w-full bg-transparent px-5 py-4 resize-none focus:outline-none text-[15px] text-slate-900 placeholder:text-slate-400 leading-relaxed min-h-[60px]"
          style={{ maxHeight: '200px' }}
        />

        {/* Toolbar */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-50">
          <div className="flex items-center gap-1">
            <FileUploadZone onFilesUploaded={files => setAttachments(p => [...p, ...files])}>
              <ToolBtn aria-label="Upload image"><Image size={18} /></ToolBtn>
            </FileUploadZone>
            <ToolBtn aria-label="Attach file"><Paperclip size={18} /></ToolBtn>
            <ToolBtn aria-label="Voice input"><Mic size={18} /></ToolBtn>
          </div>

          {isStreaming ? (
            <button
              onClick={onStopStreaming}
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-slate-100 text-slate-600 text-sm font-medium hover:bg-slate-200 transition-colors"
            >
              <Square size={14} className="fill-current" />
              Stop
            </button>
          ) : (
            <button
              onClick={() => handleSubmit()}
              disabled={!canSend}
              className={`flex items-center gap-2 px-5 py-2 rounded-xl font-medium text-sm transition-all ${
                !canSend
                  ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                  : 'bg-[#137fec] text-white shadow-md shadow-blue-200 hover:bg-[#0f6ed8] active:scale-95'
              }`}
            >
              Send
              <Send size={16} />
            </button>
          )}
        </div>
      </div>

      <p className="mt-4 text-[11px] text-center text-slate-400 uppercase tracking-wider font-medium">
        AI may make mistakes. Double-check important information.
      </p>
    </div>
  );
};

const ToolBtn: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement>> = ({ children, ...props }) => (
  <button
    type="button"
    {...props}
    className="p-2 rounded-lg text-slate-400 hover:text-[#137fec] hover:bg-blue-50 transition-all"
  >
    {children}
  </button>
);
