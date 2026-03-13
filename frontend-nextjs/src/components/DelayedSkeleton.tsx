'use client'

import React, { useState, useEffect } from 'react';
import SkeletonLoader from './SkeletonLoader';
import { MessageListSkeleton } from './MessageList';

interface DelayedSkeletonProps {
  type: 'session' | 'message';
  count?: number;
  className?: string;
  isLoading: boolean;
  delay?: number; // Default 300ms
  children?: React.ReactNode;
}

/**
 * DelayedSkeleton Component
 * 
 * Shows skeleton loaders only after a delay (default 300ms) to avoid
 * flickering for fast operations. Removes skeletons within 100ms of
 * content being available.
 * 
 * Requirements: 18.1, 18.2, 18.4, 18.5
 */
const DelayedSkeleton: React.FC<DelayedSkeletonProps> = ({
  type,
  count = 1,
  className = '',
  isLoading,
  delay = 300,
  children,
}) => {
  const [showSkeleton, setShowSkeleton] = useState(false);

  useEffect(() => {
    let timeoutId: number;

    if (isLoading) {
      // Show skeleton after delay (Requirement 18.5)
      timeoutId = window.setTimeout(() => {
        setShowSkeleton(true);
      }, delay);
    } else {
      // Hide skeleton immediately when content is available (Requirement 18.4)
      setShowSkeleton(false);
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [isLoading, delay]);

  if (isLoading && showSkeleton) {
    if (type === 'message') {
      return <MessageListSkeleton count={count} />;
    }
    return (
      <SkeletonLoader
        type={type}
        count={count}
        className={className}
      />
    );
  }

  if (!isLoading && children) {
    return <>{children}</>;
  }

  return null;
};

export default DelayedSkeleton;