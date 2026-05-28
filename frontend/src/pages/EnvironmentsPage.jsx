import { useState } from 'react'
import { useAutoRefresh, useToast } from '../hooks/useApi'
import { environmentsApi } from '../api/client'
import { LoadingState, ErrorState, EmptyState } from '../components/common/States'
import Toast from '../components/common/Toast'
import { formatDate } from '../utils/format'

const PRESET_ENVS = [
  { name: 'dev', display_name: 'Development', color: '#42a5f5' },
  { name: 'staging', display_name: 'Staging', color: '#ffca28' },
  { name: 'production', display_name: 'Production', color: '#ce93d8' },
]

function CreateEnvModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({ name: '', display_name: '', description: '', color: '#00d4ff' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePreset = (preset) => {
    setForm({ ...preset, description: '' })
  }

  const handleSubmit = async () => {
    if (!form.name || !form.display_name) return setError('Name and display name are required.')
    setLoading(true)
    try {
      await environmentsApi.create(form)
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
          <span className="modal-title">Add Environment</span>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-form">
          {error && <div style={{ color: 'var(--red)', fontSize: 12, padding: '8px 12px', background: 'var(--red-dim)', borderRadius: 6 }}>{error}</div>}
          <div>
            <div className="form-label" style={{ marginBottom: 8 }}>Quick Add</div>
            <div style={{ display: 'flex', gap: 8 }}>
              {PRESET_ENVS.map(p => (
                <button key={p.name} className="btn btn-ghost btn-sm" onClick={() => handlePreset(p)}>
                  <span style={{ color: p.color }}>◎</span> {p.name}
                </button>
              ))}
            </div>
          </div>
          <div style={{ borderTop: '1px solid var(--border)', paddingTop: 12 }} />
          <div className="form-group">
            <label className="form-label">Internal Name (slug)</label>
            <input className="form-input" placeholder="e.g. staging" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value.toLowerCase().replace(/\s+/g, '-') }))} />
          </div>
          <div className="form-group">
            <label className="form-label">Display Name</label>
            <input className="form-input" placeholder="e.g. Staging" value={form.display_name} onChange={e => setForm(p => ({ ...p, display_name: e.target.value }))} />
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <input className="form-input" placeholder="Optional description" value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} />
          </div>
          <div className="form-group">
            <label className="form-label">Color</label>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input type="color" value={form.color} onChange={e => setForm(p => ({ ...p, color: e.target.value }))} style={{ width: 40, height: 32, border: 'none', background: 'none', cursor: 'pointer' }} />
              <input className="form-input" value={form.color} onChange={e => setForm(p => ({ ...p, color: e.target.value }))} style={{ width: 120 }} />
            </div>
          </div>
          <div className="modal-actions">
            <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
              {loading ? 'Creating...' : '+ Create'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function EnvironmentsPage() {
  const [showCreate, setShowCreate] = useState(false)
  const { toast, showToast } = useToast()
  const { data: environments, loading, error, refetch } = useAutoRefresh(() => environmentsApi.list(), 60000)

  const handleDelete = async (env) => {
    if (!confirm(`Delete environment "${env.display_name}"?`)) return
    try {
      await environmentsApi.delete(env.id)
      showToast(`${env.display_name} deleted`)
      refetch()
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  if (loading) return <LoadingState message="Loading environments..." />
  if (error) return <ErrorState message={error} onRetry={refetch} />

  const list = environments || []

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Environments</h1>
          <p className="page-subtitle">Manage deployment targets (dev, staging, production)</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Add Environment</button>
      </div>

      {list.length === 0 ? (
        <div className="card">
          <EmptyState
            icon="◎"
            title="No environments defined"
            description="Add environments to organize your services and deployments."
            action={<button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Add Environment</button>}
          />
        </div>
      ) : (
        <div className="grid-2">
          {list.map(env => (
            <div key={env.id} className="card" style={{ borderLeft: `3px solid ${env.color}` }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 40,
                    height: 40,
                    borderRadius: 8,
                    background: `${env.color}20`,
                    border: `1px solid ${env.color}40`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: env.color,
                    fontSize: 18,
                  }}>◎</div>
                  <div>
                    <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 16, color: 'var(--text-primary)' }}>
                      {env.display_name}
                    </div>
                    <div style={{ fontSize: 11, color: env.color, fontFamily: 'var(--font-mono)' }}>{env.name}</div>
                  </div>
                </div>
                <button className="btn btn-danger btn-sm" onClick={() => handleDelete(env)}>✕</button>
              </div>
              {env.description && (
                <div style={{ marginTop: 12, fontSize: 12, color: 'var(--text-secondary)' }}>{env.description}</div>
              )}
              <div style={{ marginTop: 12, fontSize: 11, color: 'var(--text-muted)' }}>
                Created {formatDate(env.created_at)}
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <CreateEnvModal
          onClose={() => setShowCreate(false)}
          onSuccess={() => { setShowCreate(false); showToast('Environment created!'); refetch() }}
        />
      )}

      <Toast toast={toast} />
    </div>
  )
}
