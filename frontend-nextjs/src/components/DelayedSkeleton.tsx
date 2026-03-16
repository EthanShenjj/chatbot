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
      timeoutId = window.setTimeout(() => setShowSkeleton(true), delay);
    } else {
      setShowSkeleton(false);
    }
    return () => { if (timeoutId) clearTimeout(timeoutId); };
  }, [isLoading, delay]);

  // Always render children when not loading
  if (!isLoading) {
    return <>{children}</>;
  }

  // While loading: show skeleton overlay after delay, otherwise show nothing
  // (avoids flash for fast loads)
  if (showSkeleton) {
    if (type === 'message') return <MessageListSkeleton count={count} />;
    return <SkeletonLoader type={type} count={count} className={className} />;
  }

  // Loading but delay not reached yet — render nothing (fast path, no flicker)
  return null;
};

export default DelayedSkeleton;