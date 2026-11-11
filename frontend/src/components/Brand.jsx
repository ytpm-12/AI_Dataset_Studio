export default function Brand({ compact = false }) {
  return (
    <div className={`brand${compact ? ' brand-compact' : ''}`}>
      <span className="brand-mark" aria-hidden="true" />
      <span className="brand-copy">
        <strong>AI Dataset Studio</strong>
        <small>Data quality workspace</small>
      </span>
    </div>
  )
}
