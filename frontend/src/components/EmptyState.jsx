export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="empty-state">
      {Icon && <span className="empty-icon"><Icon /></span>}
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  )
}
