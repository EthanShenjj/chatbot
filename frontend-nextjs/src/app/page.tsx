'use client'

import { useEffect, useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { AuthPage } from '@/components/AuthPage'
import { ChatInterface } from '@/components/ChatInterface'

export default function Home() {
  const { isAuthenticated, initializeAuth } = useAuthStore()
  const [isInitialized, setIsInitialized] = useState(false)

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    initializeAuth()
    setIsInitialized(true)
  }, [initializeAuth])

  // Don't render anything until auth is initialized
  if (!isInitialized) {
    return null
  }

  // Show auth page if not authenticated
  if (!isAuthenticated) {
    return <AuthPage />
  }

  // Show main chat interface when authenticated
  return <ChatInterface />
}