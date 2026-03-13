'use client'

import { useEffect } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { AuthPage } from '@/components/AuthPage'
import { ChatInterface } from '@/components/ChatInterface'

export default function Home() {
  const { isAuthenticated, initializeAuth } = useAuthStore()

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    initializeAuth()
  }, [initializeAuth])

  // Show auth page if not authenticated
  if (!isAuthenticated) {
    return <AuthPage />
  }

  // Show main chat interface when authenticated
  return <ChatInterface />
}