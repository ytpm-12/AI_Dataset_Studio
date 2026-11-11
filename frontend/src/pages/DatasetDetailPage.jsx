import { AlertTriangle, ArrowLeft, CheckCircle2, Clock3, Columns3, Database, RefreshCw, RotateCcw, Rows3 } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { api } from '../api/client'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

export default function DatasetDetailPage() {
  const { datasetId } = useParams()
  const [dataset, setDataset] = useState(null)
  const [job, setJob] = useState(null)
  const [preview, setPreview] = useState(null)
  const [error, setError] = useState('')
  const [actionError, setActionError] = useState('')
  const [loading, setLoading] = useState(true)
  const [retrying, setRetrying] = useState(false)

  const load = useCallback(async () => {
    try {
      const payload = await fetchDatasetPage(datasetId)
      setDataset(payload.dataset)
      setJob(payload.job)
      setPreview(payload.preview)
      setError('')
    } catch (requestError) { setError(requestError.message) }
    finally { setLoading(false) }
  }, [datasetId])

  useEffect(() => {
    fetchDatasetPage(datasetId)
      .then((payload) => {
        setDataset(payload.dataset)
        setJob(payload.job)
        setPreview(payload.preview)
        setError('')
      })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false))
  }, [datasetId])
  useEffect(() => {
    if (!job || !['pending', 'processing'].includes(job.status)) return undefined
    const timer = window.setInterval(load, 5000)
    return () => window.clearInterval(timer)
  }, [job, load])

  if (loading) return <div className="center-state"><span className="spinner" />Chargement du profil</div>
  if (error) return <><Link className="back-link" to="/datasets"><ArrowLeft /> Datasets</Link><div className="alert error">{error}</div></>

  const profile = dataset.profile || {}
  const columns = profile.columns || []

  async function handleRetry() {
    setRetrying(true)
    setActionError('')
    try {
      await api.retryJob(job.id)
      await load()
    } catch (requestError) {
      await load()
      setActionError(requestError.message)
    } finally {
      setRetrying(false)
    }
  }

  return (
    <>
      <Link className="back-link" to="/datasets"><ArrowLeft /> Tous les datasets</Link>
      <PageHeader eyebrow={`${dataset.file_type.toUpperCase()} · ${dataset.original_name}`} title={dataset.name} description={`Importé le ${formatDate(dataset.created_at)}`} actions={<>{job?.status === 'failed' && <button className="button primary" onClick={handleRetry} disabled={retrying}><RotateCcw /> {retrying ? 'Relance…' : 'Relancer'}</button>}<button className="button secondary" onClick={load}><RefreshCw /> Actualiser</button></>} />
      {actionError && <div className="alert error"><AlertTriangle /> {actionError}</div>}
      <div className="detail-status"><StatusBadge status={dataset.status} />{job && <><span className="divider" /><span>Traitement <StatusBadge status={job.status} /></span><span className="progress-track" aria-label={`Progression ${job.progress}%`}><span style={{ width: `${job.progress}%` }} /></span><strong>{job.progress}%</strong></>}</div>
      {dataset.validation_errors?.length > 0 && <div className="alert error"><AlertTriangle /> <div><strong>Validation impossible</strong>{dataset.validation_errors.map((message) => <p key={message}>{message}</p>)}</div></div>}
      <section className="metric-grid compact">
        <article className="metric"><span className="metric-icon"><Rows3 /></span><div><strong>{profile.rows_profiled ?? '—'}</strong><span>Lignes profilées</span></div></article>
        <article className="metric"><span className="metric-icon blue"><Columns3 /></span><div><strong>{profile.column_count ?? '—'}</strong><span>Colonnes</span></div></article>
        <article className="metric"><span className="metric-icon success"><CheckCircle2 /></span><div><strong>{columns.filter((column) => column.missing_count === 0).length || '—'}</strong><span>Colonnes complètes</span></div></article>
        <article className="metric"><span className="metric-icon amber"><Clock3 /></span><div><strong>{profile.truncated ? 'Oui' : 'Non'}</strong><span>Profil tronqué</span></div></article>
      </section>
      {preview?.rows?.length > 0 && <section className="panel"><div className="panel-heading"><div><p className="eyebrow">Aperçu sécurisé</p><h2>Premières lignes</h2></div><span className="preview-count">{preview.returned_rows} ligne{preview.returned_rows > 1 ? 's' : ''}{preview.truncated ? ' · suite masquée' : ''}</span></div><div className="table-wrap"><table className="preview-table"><thead><tr><th>#</th>{preview.columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{preview.rows.map((row, index) => <tr key={index}><td className="mono">{index + 1}</td>{preview.columns.map((column) => <td key={column} title={formatCell(row[column])}>{formatCell(row[column])}</td>)}</tr>)}</tbody></table></div></section>}
      <section className="panel"><div className="panel-heading"><div><p className="eyebrow">Profil statistique</p><h2>Colonnes</h2></div></div>{columns.length ? <div className="table-wrap"><table><thead><tr><th>Colonne</th><th>Type détecté</th><th>Valeurs manquantes</th><th>Valeurs uniques</th><th>Exemples</th></tr></thead><tbody>{columns.map((column) => <tr key={column.name}><td className="row-title">{column.name}</td><td><span className="code-pill">{column.dtype}</span></td><td><strong>{column.missing_count}</strong><small>{column.missing_percentage}%</small></td><td>{column.unique_count ?? 'Non calculé'}</td><td><div className="sample-values">{column.sample_values.map((value) => <span key={value}>{value}</span>)}</div></td></tr>)}</tbody></table></div> : <div className="empty-state"><Database /><h3>Profil indisponible</h3><p>Le profil apparaîtra lorsque la validation sera terminée.</p></div>}</section>
    </>
  )
}

function formatDate(value) { return new Intl.DateTimeFormat('fr-FR', { dateStyle: 'long', timeStyle: 'short' }).format(new Date(value)) }

function formatCell(value) {
  if (value === null || value === undefined || value === '') return '—'
  return typeof value === 'object' ? JSON.stringify(value) : String(value)
}

async function fetchDatasetPage(datasetId) {
  const [dataset, jobsPayload] = await Promise.all([
    api.uploadDetail(datasetId),
    api.jobs(`?upload=${datasetId}`),
  ])
  const preview = dataset.status === 'validated'
    ? await api.uploadPreview(datasetId)
    : null
  return { dataset, job: jobsPayload.results[0] || null, preview }
}
