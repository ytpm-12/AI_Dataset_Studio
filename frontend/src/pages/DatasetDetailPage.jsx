import { AlertTriangle, ArrowLeft, CheckCircle2, Clock3, Columns3, Copy, Database, ExternalLink, History, RefreshCw, RotateCcw, Rows3, Search, ShieldCheck, Trash2 } from 'lucide-react'
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
  const [duplicateAnalysis, setDuplicateAnalysis] = useState(null)
  const [analyzingDuplicates, setAnalyzingDuplicates] = useState(false)
  const [transformations, setTransformations] = useState([])
  const [applyingDuplicates, setApplyingDuplicates] = useState(false)

  const load = useCallback(async () => {
    try {
      const payload = await fetchDatasetPage(datasetId)
      setDataset(payload.dataset)
      setJob(payload.job)
      setPreview(payload.preview)
      setTransformations(payload.transformations)
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
        setTransformations(payload.transformations)
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

  async function handleDuplicateAnalysis() {
    setAnalyzingDuplicates(true)
    setActionError('')
    try {
      setDuplicateAnalysis(await api.duplicatePreview(datasetId))
    } catch (requestError) {
      setActionError(requestError.message)
    } finally {
      setAnalyzingDuplicates(false)
    }
  }

  async function handleDuplicateApply() {
    const confirmed = window.confirm(
      `Créer un nouveau dataset sans ${duplicateAnalysis.duplicate_rows} doublon(s) ? Le fichier original restera intact.`,
    )
    if (!confirmed) return
    setApplyingDuplicates(true)
    setActionError('')
    try {
      await api.applyDuplicateRemoval(datasetId)
      await load()
    } catch (requestError) {
      setActionError(requestError.message)
    } finally {
      setApplyingDuplicates(false)
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
      <section className="panel cleaning-panel">
        <div className="panel-heading"><div><p className="eyebrow">Nettoyage · Prévisualisation</p><h2>Doublons exacts</h2></div><button className="button secondary" onClick={handleDuplicateAnalysis} disabled={analyzingDuplicates || dataset.status !== 'validated'}><Search /> {analyzingDuplicates ? 'Analyse…' : duplicateAnalysis ? 'Analyser à nouveau' : 'Analyser'}</button></div>
        {!duplicateAnalysis ? <div className="cleaning-intro"><span className="cleaning-icon"><Copy /></span><div><h3>Comparer toutes les colonnes</h3><p>L’analyse recherche les lignes strictement identiques et estime le résultat d’une suppression qui conserve la première occurrence.</p></div><span className="read-only-badge"><ShieldCheck /> Lecture seule</span></div> : <><div className="cleaning-summary"><article><span>Lignes analysées</span><strong>{duplicateAnalysis.analyzed_rows}</strong></article><article><span>Lignes supprimables</span><strong>{duplicateAnalysis.duplicate_rows}</strong><small>{duplicateAnalysis.duplicate_percentage}% du périmètre</small></article><article><span>Après nettoyage</span><strong>{duplicateAnalysis.rows_after_cleanup}</strong></article></div>{duplicateAnalysis.truncated && <div className="alert warning">L’analyse est limitée aux premières lignes configurées. Le nettoyage complet est bloqué pour éviter un résultat partiel.</div>}{duplicateAnalysis.duplicate_rows === 0 ? <div className="clean-result success"><CheckCircle2 /><div><strong>Aucun doublon exact détecté</strong><p>Les lignes analysées sont uniques sur l’ensemble des colonnes.</p></div></div> : <><div className="table-wrap"><table className="preview-table"><thead><tr>{Object.keys(duplicateAnalysis.sample_rows[0] || {}).map((column) => <th key={column}>{column === '_row_number' ? 'Ligne' : column}</th>)}</tr></thead><tbody>{duplicateAnalysis.sample_rows.map((row) => <tr key={row._row_number}>{Object.entries(row).map(([column, value]) => <td key={column} title={formatCell(value)}>{formatCell(value)}</td>)}</tr>)}</tbody></table></div><div className="cleaning-actions"><p><ShieldCheck /> La source sera conservée. Un nouveau dataset sera créé.</p><button className="button primary" onClick={handleDuplicateApply} disabled={duplicateAnalysis.truncated || applyingDuplicates}><Trash2 /> {applyingDuplicates ? 'Création…' : 'Créer la version nettoyée'}</button></div></>}</>}
      </section>
      {transformations.length > 0 && <section className="panel"><div className="panel-heading"><div><p className="eyebrow">Traçabilité</p><h2>Historique des transformations</h2></div><History /></div><div className="transformation-list">{transformations.map((item) => <article key={item.id}><div><strong>{item.operation_label}</strong><span>{formatDate(item.created_at)} · {item.status}</span></div><div><span>{item.summary.removed_rows ?? 0} ligne(s) supprimée(s)</span>{item.output_file && <Link className="text-link" to={`/datasets/${item.output_file}`}>Ouvrir le résultat <ExternalLink /></Link>}</div></article>)}</div></section>}
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
  const [dataset, jobsPayload, transformations] = await Promise.all([
    api.uploadDetail(datasetId),
    api.jobs(`?upload=${datasetId}`),
    api.transformations(datasetId),
  ])
  const preview = dataset.status === 'validated'
    ? await api.uploadPreview(datasetId)
    : null
  return { dataset, job: jobsPayload.results[0] || null, preview, transformations }
}
