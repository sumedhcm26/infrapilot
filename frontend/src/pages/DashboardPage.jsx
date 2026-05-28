import { useAutoRefresh } from '../hooks/useApi'
import { servicesApi, deploymentsApi, incidentsApi } from '../api/client'
import StatCard from '../components/common/StatCard'
import { LoadingState, ErrorState } from '../components/common/States'
import { formatRelative, getStatusBadgeClass, getDotClass, formatMs } from '../utils/format'

export default function DashboardPage() {
  const { data: summary, loading: sumLoading, error: sumError, refetch } = useAutoRefresh(
    () => servicesApi.summary(), 30000
  )
  const { data: services } = useAutoRefresh(() => servicesApi.list(), 30000)
  const { data: incidents } = useAutoRefresh(() => incidentsApi.list({ status: 'open', limit: 5 }), 30000)
  const { data: deployments } = useAutoRefresh(() => deploymentsApi.list({ limit: 8 }), 30000)

  if (sumLoading) return <LoadingState message="Loading dashboard..." />
  if (sumError) return <ErrorState message={sumError} onRetry={refetch} />

  const stats = summary || {}
  const svcList = services || []
  const incidentList = incidents || []
  const deployList = deployments || []

  const unhealthy = svcList.filter(s => s.is_healthy === false)

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Live system overview — auto-refreshes every 30s</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div className="dot dot-green" />
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Live</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid-4" style={{ marginBottom: 28 }}>
        <StatCard
          label="Total Services"
          value={stats.total_services ?? 0}
          sub="registered endpoints"
          icon="◈"
          color="var(--accent)"
        />
        <StatCard
          label="Healthy"
          value={stats.healthy_services ?? 0}
          sub={`of ${stats.total_services ?? 0} services`}
          icon="✓"
          color="var(--green)"
        />
        <StatCard
          label="Open Incidents"
          value={stats.open_incidents ?? 0}
          sub="require attention"
          icon="⚠"
          color={stats.open_incidents > 0 ? 'var(--red)' : 'var(--text-muted)'}
        />
        <StatCard
          label="Deployments"
          value={stats.successful_deployments ?? 0}
          sub="successful total"
          icon="↑"
          color="var(--purple)"
        />
      </div>

      <div className="grid-2">
        {/* Services Health */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 15 }}>Service Health</div>
            <a href="/services" style={{ fontSize: 11, color: 'var(--accent)' }}>View all →</a>
          </div>
          {svcList.length === 0 ? (
            <div style={{ color: 'var(--text-muted)', fontSize: 12, padding: '24px 0', textAlign: 'center' }}>
              No services registered yet.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {svcList.slice(0, 8).map(svc => (
                <div key={svc.id} style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '9px 12px',
                  borderRadius: 6,
                  background: 'var(--bg-secondary)',
                  gap: 10,
                }}>
                  <div className={`dot ${getDotClass(svc.is_healthy)}`} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 12, color: 'var(--text-primary)', fontWeight: 500, truncate: true }}>
                      {svc.name}
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {svc.url}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{formatMs(svc.last_response_time_ms)}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{svc.uptime_percentage?.toFixed(1)}% up</div>
                  </div>
                  <span className={`badge ${getStatusBadgeClass(svc.is_healthy)}`} style={{ fontSize: 9 }}>
                    {svc.is_healthy === null ? 'pending' : svc.is_healthy ? 'up' : 'down'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right column: Incidents + Recent Deployments */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Active Incidents */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 15 }}>
                Active Incidents
                {incidentList.length > 0 && (
                  <span style={{ marginLeft: 8, background: 'var(--red-dim)', color: 'var(--red)', fontSize: 10, padding: '1px 6px', borderRadius: 4, border: '1px solid rgba(255,68,68,0.2)' }}>
                    {incidentList.length}
                  </span>
                )}
              </div>
              <a href="/incidents" style={{ fontSize: 11, color: 'var(--accent)' }}>View all →</a>
            </div>
            {incidentList.length === 0 ? (
              <div style={{ color: 'var(--green)', fontSize: 12, display: 'flex', alignItems: 'center', gap: 8, padding: '8px 0' }}>
                <span>✓</span> All systems operational
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {incidentList.map(inc => (
                  <div key={inc.id} style={{
                    padding: '10px 12px',
                    background: 'var(--red-dim)',
                    borderRadius: 6,
                    borderLeft: '3px solid var(--red)',
                  }}>
                    <div style={{ fontSize: 12, color: 'var(--text-primary)', marginBottom: 3 }}>{inc.title}</div>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      <span className={`badge badge-sm ${getStatusBadgeClass(inc.severity)}`} style={{ fontSize: 9 }}>{inc.severity}</span>
                      <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{formatRelative(inc.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Deployments */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 15 }}>Recent Deployments</div>
              <a href="/deployments" style={{ fontSize: 11, color: 'var(--accent)' }}>View all →</a>
            </div>
            {deployList.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', fontSize: 12, padding: '8px 0' }}>No deployments yet.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {deployList.slice(0, 5).map(dep => (
                  <div key={dep.id} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    padding: '7px 0',
                    borderBottom: '1px solid var(--border-subtle)',
                  }}>
                    <span className={`badge ${getStatusBadgeClass(dep.status)}`} style={{ fontSize: 9, minWidth: 60, justifyContent: 'center' }}>
                      {dep.status}
                    </span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 11, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {dep.service_name} <span style={{ color: 'var(--text-muted)' }}>{dep.version}</span>
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                        {dep.environment} · {formatRelative(dep.created_at)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
