'use client'

import React from 'react';

interface SkeletonLoaderProps {
  type: 'session' | 'message';
  count?: number;
  className?: string;
}

/**
 * SkeletonLoader Component
 * 
 * Provides skeleton loading placeholders that match the layout of actual content:
 * - Session skeletons match SessionList item layout
 * - Message skeletons match MessageBubble layout
 * - Pulsing animation effect for visual feedback
 * 
 * Requirements: 18.1, 18.2, 18.4
 */
const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ 
  type, 
  count = 1, 
  className = '' 
}) => {
  const skeletons = Array.from({ length: count }, (_, index) => (
    <div key={index} className="animate-pulse">
      {type === 'session' && <SessionSkeleton />}
      {type === 'message' && <MessageSkeleton />}
    </div>
  ));

  return <div className={className}>{skeletons}</div>;
};

/**
 * SessionSkeleton matches SessionList item layout
 * - Title line (3/4 width)
 * - Timestamp line (1/2 width)
 * - Proper padding and spacing
 */
const SessionSkeleton: React.FC = () => (
  <div className="px-3 sm:px-4 py-3 border-l-2 border-transparent">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
  </div>
);

/**
 * MessageSkeleton matches MessageBubble layout
 * - Role label
 * - Multiple content lines with varying widths
 * - Timestamp
 * - Proper spacing and borders
 */
const MessageSkeleton: React.FC = () => (
  <div className="flex justify-start mb-6">
    <div className="max-w-[90%] md:max-w-[80%] border-l-2 border-l-gray-200 pl-4">
      {/* Role label skeleton */}
      <div className="h-3 bg-gray-200 rounded w-16 mb-1"></div>
      
      {/* Content skeleton - multiple lines */}
      <div className="space-y-2 mb-2">
        <div className="h-4 bg-gray-200 rounded w-full"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      </div>
      
      {/* Timestamp skeleton */}
      <div className="h-3 bg-gray-200 rounded w-12"></div>
    </div>
  </div>
);

export default SkeletonLoader;