import { useState } from 'react'
import { useAutoRefresh, useToast } from '../hooks/useApi'
import { deploymentsApi, servicesApi } from '../api/client'
import { LoadingState, ErrorState, EmptyState } from '../components/common/States'
import Toast from '../components/common/Toast'
import { formatRelative, formatDate, getStatusBadgeClass } from '../utils/format'

function CreateDeploymentModal({ services, onClose, onSuccess }) {
  const [form, setForm] = useState({
    service_id: '',
    service_name: '',
    version: '',
    environment: 'production',
    triggered_by: '',
    commit_sha: '',
    branch: '',
    notes: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const setField = (k, v) => setForm(p => ({ ...p, [k]: v }))

  const handleServiceChange = (e) => {
    const svc = services.find(s => s.id === e.target.value)
    setForm(p => ({ ...p, service_id: e.target.value, service_name: svc?.name || '' }))
  }

  const handleSubmit = async () => {
    if (!form.service_id || !form.version) return setError('Service and version are required.')
    setLoading(true)
    setError(null)
    try {
      await deploymentsApi.create(form)
      onSuccess()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal" style={{ maxWidth: 560 }}>
        <div className="modal-header">
          <span className="modal-title">Record Deployment</span>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-form">
          {error && <div style={{ color: 'var(--red)', fontSize: 12, padding: '8px 12px', background: 'var(--red-dim)', borderRadius: 6 }}>{error}</div>}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Service</label>
              <select className="form-select" value={form.service_id} onChange={handleServiceChange}>
                <option value="">Select service...</option>
                {services.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Version / Tag</label>
              <input className="form-input" placeholder="v1.2.3" value={form.version} onChange={e => setField('version', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Environment</label>
              <select className="form-select" value={form.environment} onChange={e => setField('environment', e.target.value)}>
                {['dev', 'staging', 'production'].map(e => <option key={e} value={e}>{e}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Triggered By</label>
              <input className="form-input" placeholder="GitHub Actions / your name" value={form.triggered_by} onChange={e => setField('triggered_by', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Branch</label>
              <input className="form-input" placeholder="main" value={form.branch} onChange={e => setField('branch', e.target.value)} />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Commit SHA (optional)</label>
              <input className="form-input" placeholder="abc1234" value={form.commit_sha} onChange={e => setField('commit_sha', e.target.value)} />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Notes</label>
              <textarea className="form-input" placeholder="Release notes..." value={form.notes} onChange={e => setField('notes', e.target.value)} />
            </div>
          </div>
          <div className="modal-actions">
            <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
              {loading ? 'Creating...' : '↑ Record Deployment'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function DeploymentsPage() {
  const [showCreate, setShowCreate] = useState(false)
  const { toast, showToast } = useToast()
  const { data: deployments, loading, error, refetch } = useAutoRefresh(() => deploymentsApi.list({ limit: 50 }), 30000)
  const { data: services } = useAutoRefresh(() => servicesApi.list(), 60000)

  const handleStatusUpdate = async (dep, newStatus) => {
    try {
      await deploymentsApi.update(dep.id, { status: newStatus })
      showToast(`Marked as ${newStatus}`)
      refetch()
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  if (loading) return <LoadingState message="Loading deployments..." />
  if (error) return <ErrorState message={error} onRetry={refetch} />

  const list = deployments || []
  const svcList = services || []

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Deployments</h1>
          <p className="page-subtitle">{list.length} deployment records</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>↑ Record Deployment</button>
      </div>

      {list.length === 0 ? (
        <div className="card">
          <EmptyState
            icon="↑"
            title="No deployments recorded"
            description="Track your deployment history by recording each release."
            action={<button className="btn btn-primary" onClick={() => setShowCreate(true)}>↑ Record First Deployment</button>}
          />
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Status</th>
                <th>Service</th>
                <th>Version</th>
                <th>Environment</th>
                <th>Branch</th>
                <th>Triggered By</th>
                <th>Started</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {list.map(dep => (
                <tr key={dep.id}>
                  <td>
                    <span className={`badge ${getStatusBadgeClass(dep.status)}`}>{dep.status}</span>
                  </td>
                  <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{dep.service_name}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontSize: 12 }}>{dep.version}</td>
                  <td><span className={`badge ${getStatusBadgeClass(dep.environment)}`}>{dep.environment}</span></td>
                  <td style={{ fontSize: 11, color: 'var(--text-muted)' }}>{dep.branch || '—'}</td>
                  <td style={{ fontSize: 11 }}>{dep.triggered_by || '—'}</td>
                  <td style={{ fontSize: 11 }}>{formatRelative(dep.created_at)}</td>
                  <td>
                    {dep.status === 'running' && (
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button className="btn btn-ghost btn-sm" style={{ color: 'var(--green)', borderColor: 'rgba(0,230,118,0.3)' }} onClick={() => handleStatusUpdate(dep, 'success')}>✓ Success</button>
                        <button className="btn btn-danger btn-sm" onClick={() => handleStatusUpdate(dep, 'failed')}>✕ Fail</button>
                      </div>
                    )}
                    {dep.status === 'failed' && (
                      <button className="btn btn-ghost btn-sm" onClick={() => handleStatusUpdate(dep, 'rolled_back')}>↩ Rollback</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showCreate && (
        <CreateDeploymentModal
          services={svcList}
          onClose={() => setShowCreate(false)}
          onSuccess={() => { setShowCreate(false); showToast('Deployment recorded!'); refetch() }}
        />
      )}

      <Toast toast={toast} />
    </div>
  )
}
