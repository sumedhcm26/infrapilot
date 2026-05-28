export function LoadingState({ message = 'Loading...' }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '64px 32px', gap: 12 }}>
      <div className="spinner" />
      <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>{message}</span>
    </div>
  )
}

export function ErrorState({ message, onRetry }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '64px 32px', gap: 12 }}>
      <div style={{ fontSize: 32, opacity: 0.4 }}>⚠</div>
      <div style={{ color: 'var(--red)', fontSize: 13 }}>{message}</div>
      {onRetry && (
        <button className="btn btn-ghost btn-sm" onClick={onRetry}>↺ Retry</button>
      )}
    </div>
  )
}

export function EmptyState({ icon = '◌', title, description, action }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      {title && <div style={{ fontFamily: 'var(--font-display)', fontWeight: 600, color: 'var(--text-secondary)', fontSize: 15 }}>{title}</div>}
      {description && <p>{description}</p>}
      {action}
    </div>
  )
}
