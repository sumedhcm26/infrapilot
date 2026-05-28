import { useState } from 'react'
import { useAutoRefresh, useToast } from '../hooks/useApi'
import { servicesApi } from '../api/client'
import { LoadingState, ErrorState, EmptyState } from '../components/common/States'
import Toast from '../components/common/Toast'
import { formatRelative, formatMs, getStatusBadgeClass, getDotClass } from '../utils/format'

const ENVS = ['dev', 'staging', 'production']

function AddServiceModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({ name: '', url: 'https://', description: '', environment: 'production' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const set = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  const handleSubmit = async () => {
    if (!form.name || !form.url) return setError('Name and URL are required.')
    setLoading(true)
    setError(null)
    try {
      await servicesApi.create(form)
      onSuccess()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <span className="modal-title">Register Service</span>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-form">
          {error && <div style={{ color: 'var(--red)', fontSize: 12, padding: '8px 12px', background: 'var(--red-dim)', borderRadius: 6 }}>{error}</div>}
          <div className="form-group">
            <label className="form-label">Service Name</label>
            <input className="form-input" placeholder="e.g. Payment API" value={form.name} onChange={e => set('name', e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">URL to Monitor</label>
            <input className="form-input" placeholder="https://api.example.com/health" value={form.url} onChange={e => set('url', e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Description (optional)</label>
            <input className="form-input" placeholder="Brief description..." value={form.description} onChange={e => set('description', e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Environment</label>
            <select className="form-select" value={form.environment} onChange={e => set('environment', e.target.value)}>
              {ENVS.map(e => <option key={e} value={e}>{e}</option>)}
            </select>
          </div>
          <div className="modal-actions">
            <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
              {loading ? 'Registering...' : '+ Register'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ServicesPage() {
  const [showAdd, setShowAdd] = useState(false)
  const [checking, setChecking] = useState({})
  const { toast, showToast } = useToast()
  const { data: services, loading, error, refetch } = useAutoRefresh(() => servicesApi.list(), 30000)

  const handleCheck = async (svc) => {
    setChecking(prev => ({ ...prev, [svc.id]: true }))
    try {
      await servicesApi.check(svc.id)
      showToast(`Health check complete for ${svc.name}`)
      refetch()
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setChecking(prev => ({ ...prev, [svc.id]: false }))
    }
  }

  const handleDelete = async (svc) => {
    if (!confirm(`Delete "${svc.name}"? This cannot be undone.`)) return
    try {
      await servicesApi.delete(svc.id)
      showToast(`${svc.name} removed`)
      refetch()
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  if (loading) return <LoadingState message="Loading services..." />
  if (error) return <ErrorState message={error} onRetry={refetch} />

  const list = services || []

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Services</h1>
          <p className="page-subtitle">{list.length} registered endpoint{list.length !== 1 ? 's' : ''}</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAdd(true)}>+ Register Service</button>
      </div>

      {list.length === 0 ? (
        <div className="card">
          <EmptyState
            icon="◈"
            title="No services yet"
            description="Register a service URL to start monitoring uptime and response times."
            action={<button className="btn btn-primary" onClick={() => setShowAdd(true)}>+ Register First Service</button>}
          />
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Status</th>
                <th>Name</th>
                <th>URL</th>
                <th>Environment</th>
                <th>Response</th>
                <th>Uptime</th>
                <th>Last Checked</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {list.map(svc => (
                <tr key={svc.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                      <div className={`dot ${getDotClass(svc.is_healthy)}`} />
                      <span className={`badge ${getStatusBadgeClass(svc.is_healthy)}`} style={{ fontSize: 9 }}>
                        {svc.is_healthy === null ? 'pending' : svc.is_healthy ? 'up' : 'down'}
                      </span>
                    </div>
                  </td>
                  <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{svc.name}</td>
                  <td>
                    <a href={svc.url} target="_blank" rel="noreferrer" style={{ fontSize: 11, maxWidth: 200, display: 'inline-block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--accent)' }}>
                      {svc.url}
                    </a>
                  </td>
                  <td>
                    <span className={`badge ${getStatusBadgeClass(svc.environment)}`}>{svc.environment}</span>
                  </td>
                  <td style={{ color: svc.last_response_time_ms > 500 ? 'var(--yellow)' : 'var(--text-secondary)' }}>
                    {formatMs(svc.last_response_time_ms)}
                    {svc.last_status_code && (
                      <span style={{ marginLeft: 6, fontSize: 10, color: 'var(--text-muted)' }}>
                        HTTP {svc.last_status_code}
                      </span>
                    )}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <div style={{ width: 48, height: 4, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
                        <div style={{ width: `${svc.uptime_percentage}%`, height: '100%', background: svc.uptime_percentage > 95 ? 'var(--green)' : svc.uptime_percentage > 80 ? 'var(--yellow)' : 'var(--red)', transition: 'width 0.3s' }} />
                      </div>
                      <span style={{ fontSize: 11 }}>{svc.uptime_percentage?.toFixed(1)}%</span>
                    </div>
                  </td>
                  <td style={{ fontSize: 11 }}>{formatRelative(svc.last_checked_at)}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => handleCheck(svc)}
                        disabled={checking[svc.id]}
                      >
                        {checking[svc.id] ? '...' : '↺ Check'}
                      </button>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDelete(svc)}>✕</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showAdd && (
        <AddServiceModal
          onClose={() => setShowAdd(false)}
          onSuccess={() => { setShowAdd(false); showToast('Service registered!'); refetch() }}
        />
      )}

      <Toast toast={toast} />
    </div>
  )
}
