'use client'

import React, { useState, useCallback, useRef } from 'react';
import type { FileUploadZoneProps } from '@/types/components';
import type { FileUploadResponse, FileUploadError } from '@/types/api';
import type { ContentBlock } from '@/types/message';
import { fetchWithAuth } from '@/services/apiClient';

const ALLOWED_TYPES = [
  'image/png',
  'image/jpeg',
  'image/gif',
  'application/pdf',
  'audio/mpeg',
  'audio/wav',
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

interface FileUploadZonePropsLocal {
  onFilesUploaded: (files: ContentBlock[]) => void;
  maxFileSize?: number;
  allowedTypes?: string[];
  children: React.ReactNode;
}

export const FileUploadZone: React.FC<FileUploadZonePropsLocal> = ({
  onFilesUploaded,
  maxFileSize = MAX_FILE_SIZE,
  allowedTypes = ALLOWED_TYPES,
  children,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dragCounter = useRef(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback(
    (file: File): string | null => {
      if (!allowedTypes.includes(file.type)) {
        return `Invalid file type: ${file.type}`;
      }

      if (file.size > maxFileSize) {
        const maxSizeMB = (maxFileSize / (1024 * 1024)).toFixed(1);
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(1);
        return `File too large: ${fileSizeMB}MB (max: ${maxSizeMB}MB)`;
      }

      return null;
    },
    [allowedTypes, maxFileSize]
  );

  const uploadFile = async (file: File): Promise<ContentBlock | null> => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetchWithAuth('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData: FileUploadError = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }

      const data: FileUploadResponse = await response.json();

      if (file.type.startsWith('image/')) {
        return {
          type: 'image_url',
          image_url: { url: data.url }
        };
      } else if (file.type.startsWith('audio/')) {
        return {
          type: 'audio',
          audio: { url: data.url }
        };
      } else {
        return {
          type: 'file',
          file: { url: data.url, name: data.filename }
        };
      }
    } catch (err) {
      throw err;
    }
  };
  const handleFiles = async (files: FileList | File[]) => {
    setError(null);
    const fileArray = Array.from(files);

    const validationErrors: string[] = [];
    for (const file of fileArray) {
      const validationError = validateFile(file);
      if (validationError) {
        validationErrors.push(`${file.name}: ${validationError}`);
      }
    }

    if (validationErrors.length > 0) {
      setError(validationErrors.join('\n'));
      return;
    }

    setIsUploading(true);
    try {
      const uploadPromises = fileArray.map((file) => uploadFile(file));
      const results = await Promise.all(uploadPromises);
      const successfulUploads = results.filter(
        (result): result is ContentBlock => result !== null
      );

      if (successfulUploads.length > 0) {
        onFilesUploaded(successfulUploads);
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Upload failed';
      setError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFiles(files);
    }
  };

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current++;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current--;
    if (dragCounter.current === 0) {
      setIsDragging(false);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      dragCounter.current = 0;

      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        handleFiles(files);
      }
    },
    [handleFiles]
  );

  return (
    <div
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className="relative"
    >
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={allowedTypes.join(',')}
        onChange={handleFileInputChange}
        className="hidden"
      />
      
      <div onClick={handleClick}>
        {children}
      </div>

      {isDragging && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-blue-50 border-2 border-dashed border-blue-400 rounded-lg">
          <div className="text-blue-600 font-medium">Drop files here</div>
        </div>
      )}

      {isUploading && (
        <div className="absolute inset-0 z-40 flex items-center justify-center bg-white bg-opacity-90 rounded-lg">
          <div className="text-gray-600">Uploading...</div>
        </div>
      )}

      {error && (
        <div className="absolute top-full left-0 right-0 mt-2 p-2 bg-red-50 border border-red-200 rounded text-red-600 text-sm whitespace-pre-line z-50">
          {error}
        </div>
      )}
    </div>
  );
};