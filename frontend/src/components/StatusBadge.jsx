const labels = {
  uploaded: 'Importé',
  validation_pending: 'En attente',
  pending: 'En attente',
  processing: 'En traitement',
  validated: 'Validé',
  completed: 'Terminé',
  invalid: 'Invalide',
  failed: 'Échec',
  cancelled: 'Annulé',
}

export default function StatusBadge({ status }) {
  return <span className={`status status-${status}`}>{labels[status] || status}</span>
}
