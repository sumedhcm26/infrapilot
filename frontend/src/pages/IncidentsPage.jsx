import { useState } from 'react'
import { useAutoRefresh, useToast } from '../hooks/useApi'
import { incidentsApi } from '../api/client'
import { LoadingState, ErrorState, EmptyState } from '../components/common/States'
import Toast from '../components/common/Toast'
import { formatRelative, formatDate, getStatusBadgeClass } from '../utils/format'

export default function IncidentsPage() {
  const [filter, setFilter] = useState('all')
  const { toast, showToast } = useToast()
  const { data: incidents, loading, error, refetch } = useAutoRefresh(
    () => incidentsApi.list({ limit: 100 }), 30000
  )

  const handleUpdate = async (inc, newStatus) => {
    try {
      await incidentsApi.update(inc.id, {
        status: newStatus,
        resolution_notes: newStatus === 'resolved' ? 'Manually resolved via dashboard' : undefined,
      })
      showToast(`Incident ${newStatus}`)
      refetch()
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  if (loading) return <LoadingState message="Loading incidents..." />
  if (error) return <ErrorState message={error} onRetry={refetch} />

  const all = incidents || []
  const filtered = filter === 'all' ? all : all.filter(i => i.status === filter)

  const counts = {
    all: all.length,
    open: all.filter(i => i.status === 'open').length,
    acknowledged: all.filter(i => i.status === 'acknowledged').length,
    resolved: all.filter(i => i.status === 'resolved').length,
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Incidents</h1>
          <p className="page-subtitle">
            {counts.open > 0
              ? <span style={{ color: 'var(--red)' }}>{counts.open} open incident{counts.open !== 1 ? 's' : ''} — requires attention</span>
              : <span style={{ color: 'var(--green)' }}>All clear — no open incidents</span>
            }
          </p>
        </div>
      </div>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 20 }}>
        {['all', 'open', 'acknowledged', 'resolved'].map(f => (
          <button
            key={f}
            className={`btn ${filter === f ? 'btn-primary' : 'btn-ghost'} btn-sm`}
            onClick={() => setFilter(f)}
            style={{ textTransform: 'capitalize' }}
          >
            {f} <span style={{ opacity: 0.6 }}>({counts[f]})</span>
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="card">
          <EmptyState
            icon="✓"
            title={filter === 'open' ? 'No open incidents' : 'No incidents found'}
            description={filter === 'open' ? 'All systems are operational.' : 'Incidents are created automatically when services go down.'}
          />
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {filtered.map(inc => (
            <div key={inc.id} className="card" style={{
              borderLeft: inc.status === 'open' ? '3px solid var(--red)' : inc.status === 'acknowledged' ? '3px solid var(--yellow)' : '3px solid var(--green)',
            }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
                    <span className={`badge ${getStatusBadgeClass(inc.status)}`}>{inc.status}</span>
                    <span className={`badge ${getStatusBadgeClass(inc.severity)}`}>{inc.severity}</span>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>#{inc.id.slice(0, 8)}</span>
                  </div>
                  <div style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 15, color: 'var(--text-primary)', marginBottom: 4 }}>
                    {inc.title}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8 }}>
                    Service: <strong style={{ color: 'var(--text-primary)' }}>{inc.service_name}</strong>
                    {inc.trigger_status_code && <span style={{ marginLeft: 8, color: 'var(--red)' }}>HTTP {inc.trigger_status_code}</span>}
                  </div>
                  {inc.description && (
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>{inc.description}</div>
                  )}
                  <div style={{ display: 'flex', gap: 16, fontSize: 11, color: 'var(--text-muted)' }}>
                    <span>Created {formatRelative(inc.created_at)}</span>
                    {inc.resolved_at && <span>Resolved {formatRelative(inc.resolved_at)}</span>}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
                  {inc.status === 'open' && (
                    <>
                      <button className="btn btn-ghost btn-sm" style={{ color: 'var(--yellow)', borderColor: 'rgba(255,202,40,0.3)' }} onClick={() => handleUpdate(inc, 'acknowledged')}>
                        Acknowledge
                      </button>
                      <button className="btn btn-ghost btn-sm" style={{ color: 'var(--green)', borderColor: 'rgba(0,230,118,0.3)' }} onClick={() => handleUpdate(inc, 'resolved')}>
                        Resolve
                      </button>
                    </>
                  )}
                  {inc.status === 'acknowledged' && (
                    <button className="btn btn-ghost btn-sm" style={{ color: 'var(--green)', borderColor: 'rgba(0,230,118,0.3)' }} onClick={() => handleUpdate(inc, 'resolved')}>
                      ✓ Resolve
                    </button>
                  )}
                </div>
              </div>
              {inc.resolution_notes && (
                <div style={{ marginTop: 12, padding: '8px 12px', background: 'var(--green-dim)', borderRadius: 6, fontSize: 12, color: 'var(--green)' }}>
                  Resolution: {inc.resolution_notes}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <Toast toast={toast} />
    </div>
  )
}
