import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { healthApi } from '../../api/client'

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: '▦' },
  { path: '/services', label: 'Services', icon: '◈' },
  { path: '/deployments', label: 'Deployments', icon: '↑' },
  { path: '/incidents', label: 'Incidents', icon: '⚠' },
  { path: '/environments', label: 'Environments', icon: '◎' },
]

export default function Layout() {
  const [apiStatus, setApiStatus] = useState('checking')
  const location = useLocation()

  // Check backend health on mount and every 60s
  useEffect(() => {
    const check = async () => {
      try {
        await healthApi.check()
        setApiStatus('online')
      } catch {
        setApiStatus('offline')
      }
    }
    check()
    const interval = setInterval(check, 60000)
    return () => clearInterval(interval)
  }, [])

  const currentPage = NAV_ITEMS.find(item => location.pathname.startsWith(item.path))

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside style={{
        width: 220,
        minHeight: '100vh',
        background: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        top: 0,
        left: 0,
        bottom: 0,
        zIndex: 100,
      }}>
        {/* Logo */}
        <div style={{ padding: '24px 20px 20px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 32,
              height: 32,
              background: 'var(--accent)',
              borderRadius: 6,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#000',
              fontWeight: 800,
              fontSize: 14,
              fontFamily: 'var(--font-display)',
              flexShrink: 0,
            }}>IP</div>
            <div>
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 15, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>InfraPilot</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.05em' }}>v1.0.0</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: '12px 0' }}>
          <div style={{ padding: '0 12px', marginBottom: 4 }}>
            <div style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.12em', padding: '6px 8px' }}>Navigation</div>
          </div>
          {NAV_ITEMS.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '9px 20px',
                margin: '1px 8px',
                borderRadius: 6,
                textDecoration: 'none',
                fontSize: 13,
                fontFamily: 'var(--font-mono)',
                transition: 'all 0.15s',
                color: isActive ? 'var(--accent)' : 'var(--text-secondary)',
                background: isActive ? 'var(--accent-glow)' : 'transparent',
                borderLeft: isActive ? '2px solid var(--accent)' : '2px solid transparent',
              })}
            >
              <span style={{ fontSize: 14, opacity: 0.8 }}>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* API Status indicator at bottom */}
        <div style={{
          padding: '16px 20px',
          borderTop: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
        }}>
          <div className={`dot ${apiStatus === 'online' ? 'dot-green' : apiStatus === 'offline' ? 'dot-red' : 'dot-yellow'}`} />
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>API Backend</div>
            <div style={{ fontSize: 10, color: apiStatus === 'online' ? 'var(--green)' : apiStatus === 'offline' ? 'var(--red)' : 'var(--yellow)' }}>
              {apiStatus}
            </div>
          </div>
        </div>
      </aside>

      {/* Main content area */}
      <main style={{ flex: 1, marginLeft: 220, minHeight: '100vh' }}>
        {/* Top bar */}
        <div style={{
          height: 56,
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 32px',
          background: 'rgba(10,13,18,0.8)',
          backdropFilter: 'blur(8px)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          gap: 8,
        }}>
          <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>InfraPilot</span>
          <span style={{ color: 'var(--border)', fontSize: 12 }}>/</span>
          <span style={{ color: 'var(--text-primary)', fontSize: 12, fontFamily: 'var(--font-display)', fontWeight: 600 }}>
            {currentPage?.label || 'Dashboard'}
          </span>
          <div style={{ flex: 1 }} />
          {/* Clock */}
          <ClockDisplay />
        </div>

        {/* Page content */}
        <Outlet />
      </main>
    </div>
  )
}

function ClockDisplay() {
  const [time, setTime] = useState(new Date())
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  return (
    <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
      {time.toUTCString().replace(' GMT', ' UTC')}
    </div>
  )
}
