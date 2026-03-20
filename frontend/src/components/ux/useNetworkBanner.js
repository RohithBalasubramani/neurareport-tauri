/**
 * Hook for NetworkStatusBanner state management
 * Handles retry logic, status transitions, and periodic connectivity checks
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'

// Status types
export const NetworkStatus = {
  ONLINE: 'online',
  OFFLINE: 'offline',
  RECONNECTING: 'reconnecting',
  SERVER_DOWN: 'server_down',
}

export default function useNetworkBanner({ onRetry } = {}) {
  const { isOnline, checkConnectivity, checkServer } = useNetworkStatus()
  const [status, setStatus] = useState(NetworkStatus.ONLINE)
  const [isRetrying, setIsRetrying] = useState(false)
  const [showBanner, setShowBanner] = useState(false)
  const [wasOffline, setWasOffline] = useState(false)
  const successTimeoutRef = useRef(null)
  const prevOnlineRef = useRef(isOnline)

  // Handle retry
  const handleRetry = useCallback(async () => {
    setIsRetrying(true)
    setStatus(NetworkStatus.RECONNECTING)

    try {
      const browserOnline = await checkConnectivity()

      if (browserOnline) {
        const serverUp = await checkServer()

        if (serverUp) {
          setStatus(NetworkStatus.ONLINE)
          setWasOffline(true)
          // Keep banner briefly to show success
          clearTimeout(successTimeoutRef.current)
          successTimeoutRef.current = setTimeout(() => {
            setShowBanner(false)
            setWasOffline(false)
          }, 2000)
        } else {
          setStatus(NetworkStatus.SERVER_DOWN)
        }
      } else {
        setStatus(NetworkStatus.OFFLINE)
      }
    } finally {
      setIsRetrying(false)
    }

    onRetry?.()
  }, [checkConnectivity, checkServer, onRetry])

  // Monitor network status - only retry on actual offline-to-online transitions
  useEffect(() => {
    if (!isOnline) {
      setStatus(NetworkStatus.OFFLINE)
      setShowBanner(true)
    } else if (!prevOnlineRef.current) {
      // Transitioning from offline to online, verify with server
      handleRetry()
    }
    prevOnlineRef.current = isOnline
  }, [isOnline, handleRetry])

  // Periodic check when offline
  useEffect(() => {
    if (status === NetworkStatus.OFFLINE || status === NetworkStatus.SERVER_DOWN) {
      const interval = setInterval(handleRetry, 30000) // Check every 30s
      return () => clearInterval(interval)
    }
  }, [status, handleRetry])

  // Cleanup success timeout on unmount
  useEffect(() => {
    return () => clearTimeout(successTimeoutRef.current)
  }, [])

  return {
    isOnline,
    status,
    isRetrying,
    showBanner,
    wasOffline,
    handleRetry,
  }
}
