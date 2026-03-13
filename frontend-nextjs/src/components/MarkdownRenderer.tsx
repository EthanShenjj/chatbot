'use client'

import React, { useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import Prism from 'prismjs';
import type { MarkdownRendererProps } from '@/types/components';
import 'katex/dist/katex.min.css';
import 'prismjs/themes/prism-tomorrow.css';
import './MarkdownRenderer.css';

// Import Prism language support
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-tsx';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-java';
import 'prismjs/components/prism-c';
import 'prismjs/components/prism-cpp';
import 'prismjs/components/prism-csharp';
import 'prismjs/components/prism-go';
import 'prismjs/components/prism-rust';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-yaml';
import 'prismjs/components/prism-markdown';

/**
 * MarkdownRenderer component
 * 
 * Converts markdown text to formatted HTML with:
 * - Syntax highlighting via Prism.js
 * - LaTeX math rendering via KaTeX
 * - HTML sanitization (handled by react-markdown)
 * - Inline image rendering
 * 
 * Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
 */
export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = '' }) => {
  // Apply syntax highlighting after render
  useEffect(() => {
    Prism.highlightAll();
  }, [content]);

  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          // Custom code block renderer with syntax highlighting
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            const isInline = !children || typeof children === 'string';
            
            if (!isInline && language) {
              return (
                <pre className={`language-${language}`}>
                  <code className={`language-${language}`} {...props}>
                    {children}
                  </code>
                </pre>
              );
            }
            
            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          // Custom image renderer
          img({ src, alt, ...props }) {
            return (
              <img
                src={src}
                alt={alt || ''}
                className="max-w-full h-auto rounded"
                loading="lazy"
                {...props}
              />
            );
          },
          // Custom link renderer with security
          a({ href, children, ...props }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
                {...props}
              >
                {children}
              </a>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};