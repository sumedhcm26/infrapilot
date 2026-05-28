/**
 * StatCard - Dashboard metric card
 */
export default function StatCard({ label, value, sub, color = 'var(--accent)', icon }) {
  return (
    <div className="card" style={{ position: 'relative', overflow: 'hidden' }}>
      {/* Subtle accent line at top */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: color, opacity: 0.6 }} />
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
          {label}
        </div>
        {icon && (
          <div style={{ fontSize: 18, opacity: 0.4 }}>{icon}</div>
        )}
      </div>
      <div style={{
        fontFamily: 'var(--font-display)',
        fontSize: 36,
        fontWeight: 800,
        color,
        lineHeight: 1,
        marginBottom: 6,
        letterSpacing: '-0.03em',
      }}>
        {value}
      </div>
      {sub && (
        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{sub}</div>
      )}
    </div>
  )
}
