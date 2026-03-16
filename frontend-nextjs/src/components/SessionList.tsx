'use client'

import React from 'react';
import { useSessionStore } from '@/stores/sessionStore';
import DelayedSkeleton from './DelayedSkeleton';
import { MessageSquare, Trash2 } from 'lucide-react';

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} mins ago`;
  if (diffHours < 24) return `${diffHours} hours ago`;
  if (diffDays < 7) return `${diffDays} days ago`;
  return date.toLocaleDateString();
};

interface SessionItemProps {
  session: { id: string; title: string; updated_at: string };
  isSelected: boolean;
  onClick: () => void;
  onDelete: (e: React.MouseEvent) => void;
}

const SessionItem: React.FC<SessionItemProps> = ({ session, isSelected, onClick, onDelete }) => {
  const title = session.title || 'New conversation';

  return (
    <div className="relative group">
      <button
        onClick={onClick}
        className={`
          w-full flex items-start gap-3 px-3 py-2.5 text-sm rounded-lg transition-colors text-left pr-10
          ${isSelected ? 'bg-blue-50 text-[#137fec]' : 'text-slate-600 hover:bg-slate-50'}
        `}
      >
        <MessageSquare size={16} className={`mt-0.5 shrink-0 ${isSelected ? 'text-[#137fec]' : 'text-slate-400'}`} />
        <div className="min-w-0">
          <p className="font-medium truncate">{title}</p>
          <p className="text-[11px] text-slate-400">{formatDate(session.updated_at)}</p>
        </div>
      </button>
      <button
        onClick={onDelete}
        className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all z-10"
        aria-label="Delete session"
      >
        <Trash2 size={14} />
      </button>
    </div>
  );
};

export const SessionList: React.FC<{ searchTerm?: string }> = ({ searchTerm = '' }) => {
  const { sessions, currentSessionId, isLoadingSessions, selectSession, deleteSession } = useSessionStore();

  const handleDelete = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    try {
      await deleteSession(sessionId);
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  // Filter sessions based on search term
  const filteredSessions = React.useMemo(() => {
    if (!searchTerm.trim()) return sessions;
    
    const lowerSearch = searchTerm.toLowerCase();
    return sessions.filter(session => 
      session.title.toLowerCase().includes(lowerSearch)
    );
  }, [sessions, searchTerm]);

  return (
    <div className="flex flex-col">
      <DelayedSkeleton type="session" count={5} isLoading={isLoadingSessions} delay={300}>
        <div className="space-y-0.5">
          {filteredSessions.length === 0 ? (
            <div className="px-3 py-6 text-center">
              <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-gray-100 flex items-center justify-center">
                <MessageSquare className="w-5 h-5 text-gray-400" />
              </div>
              <p className="text-xs text-gray-500">
                {searchTerm ? 'No results found' : 'No sessions yet'}
              </p>
            </div>
          ) : (
            filteredSessions.map((session) => (
              <SessionItem
                key={session.id}
                session={session}
                isSelected={session.id === currentSessionId}
                onClick={() => selectSession(session.id).catch(console.error)}
                onDelete={(e) => handleDelete(e, session.id)}
              />
            ))
          )}
        </div>
      </DelayedSkeleton>
    </div>
  );
};
