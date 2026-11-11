import { Activity, ArrowRight, CheckCircle2, Database, FolderKanban, Upload } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { api } from '../api/client'
import EmptyState from '../components/EmptyState'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

export default function DashboardPage() {
  const [data, setData] = useState({ projects: [], uploads: [], jobs: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.projects(), api.uploads(), api.jobs()])
      .then(([projects, uploads, jobs]) => setData({ projects: projects.results, uploads: uploads.results, jobs: jobs.results }))
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false))
  }, [])

  const validated = data.uploads.filter((upload) => upload.status === 'validated').length
  const activeJobs = data.jobs.filter((job) => ['pending', 'processing'].includes(job.status)).length

  return (
    <>
      <PageHeader eyebrow="Workspace" title="Vue d’ensemble" description="Suivez la préparation de vos datasets et les traitements en cours." actions={<Link className="button primary" to="/datasets"><Upload /> Nouvel import</Link>} />
      {error && <div className="alert error">{error}</div>}
      <section className="metric-grid" aria-label="Indicateurs">
        <article className="metric"><span className="metric-icon"><FolderKanban /></span><div><strong>{loading ? '—' : data.projects.length}</strong><span>Projets</span></div></article>
        <article className="metric"><span className="metric-icon blue"><Database /></span><div><strong>{loading ? '—' : data.uploads.length}</strong><span>Datasets</span></div></article>
        <article className="metric"><span className="metric-icon success"><CheckCircle2 /></span><div><strong>{loading ? '—' : validated}</strong><span>Validés</span></div></article>
        <article className="metric"><span className="metric-icon amber"><Activity /></span><div><strong>{loading ? '—' : activeJobs}</strong><span>Jobs actifs</span></div></article>
      </section>
      <section className="panel">
        <div className="panel-heading"><div><p className="eyebrow">Activité</p><h2>Imports récents</h2></div><Link className="text-link" to="/datasets">Tout afficher <ArrowRight /></Link></div>
        {loading ? <div className="loading-row"><span className="spinner" />Chargement des imports</div> : data.uploads.length ? (
          <div className="table-wrap"><table><thead><tr><th>Dataset</th><th>Format</th><th>Taille</th><th>Statut</th><th>Date</th></tr></thead><tbody>{data.uploads.slice(0, 6).map((upload) => <tr key={upload.id}><td><Link className="row-title" to={`/datasets/${upload.id}`}>{upload.name}</Link><small>{upload.original_name}</small></td><td className="mono">{upload.file_type.toUpperCase()}</td><td>{formatBytes(upload.size)}</td><td><StatusBadge status={upload.status} /></td><td>{formatDate(upload.created_at)}</td></tr>)}</tbody></table></div>
        ) : <EmptyState icon={Database} title="Aucun dataset" description="Votre premier import apparaîtra ici." action={<Link className="button secondary" to="/datasets">Importer un fichier</Link>} />}
      </section>
    </>
  )
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} o`
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} Ko`
  return `${(bytes / 1024 ** 2).toFixed(1)} Mo`
}

function formatDate(value) { return new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium' }).format(new Date(value)) }
