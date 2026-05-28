/**
 * Custom React Hooks
 * ==================
 * Custom hooks extract and reuse stateful logic.
 * Each hook manages loading, error, and data state for API calls.
 */

import { useState, useEffect, useCallback } from 'react'

/**
 * Generic data fetcher hook.
 * Handles loading/error states automatically.
 *
 * Usage:
 *   const { data, loading, error, refetch } = useApi(() => servicesApi.list())
 */
export function useApi(fetchFn, deps = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetchFn()
      setData(response.data)
    } catch (err) {
      setError(err.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }, deps) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

/**
 * Auto-refreshing data hook.
 * Calls the API every `intervalMs` milliseconds.
 * Great for live dashboards without WebSockets.
 */
export function useAutoRefresh(fetchFn, intervalMs = 30000, deps = []) {
  const { data, loading, error, refetch } = useApi(fetchFn, deps)

  useEffect(() => {
    const interval = setInterval(refetch, intervalMs)
    return () => clearInterval(interval) // Cleanup on unmount
  }, [refetch, intervalMs])

  return { data, loading, error, refetch }
}

/**
 * Toast notification hook.
 */
export function useToast() {
  const [toast, setToast] = useState(null)

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3500)
  }, [])

  return { toast, showToast }
}
