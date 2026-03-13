'use client'

import React from 'react';
import { useSessionStore } from '@/stores/sessionStore';
import { DelayedSkeleton } from './DelayedSkeleton';
import { MessageSquare } from 'lucide-react';

/**
 * SessionList Component - Clean Gemini-inspired Style
 */
export const SessionList: React.FC = () => {
  const {
    sessions,
    currentSessionId,
    isLoadingSessions,
    selectSession,
    createSession,
  } = useSessionStore();

  const handleSessionClick = async (sessionId: string) => {
    try {
      await selectSession(sessionId);
    } catch (error) {
      console.error('Failed to select session:', error);
    }
  };

  const handleNewSession = async () => {
    try {
      await createSession();
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <DelayedSkeleton
        type="session"
        count={5}
        isLoading={isLoadingSessions}
        delay={300}
      >
        <div className="space-y-1">
          {sessions.length === 0 ? (
            <div className="px-3 py-8 text-center">
              <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-slate-100 flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-slate-400" />
              </div>
              <p className="text-sm text-slate-500">No sessions yet</p>
              <p className="text-xs text-slate-400 mt-1">Start a conversation to begin</p>
            </div>
          ) : (
            sessions.map((session) => (
              <SessionItem
                key={session.id}
                session={session}
                isSelected={session.id === currentSessionId}
                onClick={() => handleSessionClick(session.id)}
              />
            ))
          )}
        </div>
      </DelayedSkeleton>
    </div>
  );
};
/**
 * SessionItem Component - Clean Gemini-inspired Style
 */
interface SessionItemProps {
  session: {
    id: string;
    title: string;
    updated_at: string;
  };
  isSelected: boolean;
  onClick: () => void;
}

const SessionItem: React.FC<SessionItemProps> = ({ session, isSelected, onClick }) => {
  const title = session.title || 'New conversation';
  const truncatedTitle = title.length > 40
    ? title.substring(0, 40) + '...'
    : title;

  return (
    <button
      onClick={onClick}
      className={`
        w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-600 hover:text-slate-900 transition-colors text-left rounded-lg
        ${isSelected ? 'bg-white shadow-sm text-slate-900' : 'hover:bg-slate-200/50'}
      `}
    >
      <span className="truncate">{truncatedTitle}</span>
    </button>
  );
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) {
    return 'Just now';
  } else if (diffMins < 60) {
    return `${diffMins}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    return date.toLocaleDateString();
  }
};