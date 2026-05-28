/**
 * Formatting utilities
 */

import { formatDistanceToNow, format } from 'date-fns'

export function formatRelative(dateStr) {
  if (!dateStr) return '—'
  try {
    return formatDistanceToNow(new Date(dateStr), { addSuffix: true })
  } catch {
    return dateStr
  }
}

export function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    return format(new Date(dateStr), 'MMM d, yyyy HH:mm')
  } catch {
    return dateStr
  }
}

export function formatMs(ms) {
  if (ms === null || ms === undefined) return '—'
  if (ms < 1000) return `${Math.round(ms)}ms`
  return `${(ms / 1000).toFixed(2)}s`
}

export function getStatusBadgeClass(status) {
  const map = {
    // Service health
    true: 'badge-green',
    false: 'badge-red',
    // Deployment status
    success: 'badge-green',
    running: 'badge-blue',
    pending: 'badge-yellow',
    failed: 'badge-red',
    rolled_back: 'badge-orange',
    // Incident status
    open: 'badge-red',
    acknowledged: 'badge-yellow',
    resolved: 'badge-green',
    // Severity
    critical: 'badge-red',
    high: 'badge-orange',
    medium: 'badge-yellow',
    low: 'badge-blue',
    // Environment
    production: 'badge-purple',
    staging: 'badge-blue',
    dev: 'badge-gray',
  }
  return map[status] ?? 'badge-gray'
}

export function getDotClass(isHealthy) {
  if (isHealthy === null || isHealthy === undefined) return 'dot-gray'
  return isHealthy ? 'dot-green' : 'dot-red'
}
