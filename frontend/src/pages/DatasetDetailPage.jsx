import { AlertTriangle, ArrowLeft, Bot, CheckCircle2, Clock3, Columns3, Copy, Database, Download, Droplets, ExternalLink, Gauge, History, RefreshCw, RotateCcw, Rows3, Search, ShieldCheck, Shuffle, Sparkles, Trash2 } from 'lucide-react'
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
      <MissingValuesPanel datasetId={datasetId} datasetStatus={dataset.status} onApplied={load} setActionError={setActionError} />
      <TypeConversionPanel datasetId={datasetId} datasetStatus={dataset.status} onApplied={load} setActionError={setActionError} />
      <AIRecommendationPanel datasetId={datasetId} datasetStatus={dataset.status} setActionError={setActionError} />
      <QualityAndExportPanel datasetId={datasetId} datasetStatus={dataset.status} setActionError={setActionError} />
      {transformations.length > 0 && <section className="panel"><div className="panel-heading"><div><p className="eyebrow">Traçabilité</p><h2>Historique des transformations</h2></div><History /></div><div className="transformation-list">{transformations.map((item) => <article key={item.id}><div><strong>{item.operation_label}</strong><span>{formatDate(item.created_at)} · {item.status}</span></div><div><span>{item.summary.removed_rows ?? 0} ligne(s) supprimée(s)</span>{item.output_file && <Link className="text-link" to={`/datasets/${item.output_file}`}>Ouvrir le résultat <ExternalLink /></Link>}</div></article>)}</div></section>}
      <section className="panel"><div className="panel-heading"><div><p className="eyebrow">Profil statistique</p><h2>Colonnes</h2></div></div>{columns.length ? <div className="table-wrap"><table><thead><tr><th>Colonne</th><th>Type détecté</th><th>Valeurs manquantes</th><th>Valeurs uniques</th><th>Exemples</th></tr></thead><tbody>{columns.map((column) => <tr key={column.name}><td className="row-title">{column.name}</td><td><span className="code-pill">{column.dtype}</span></td><td><strong>{column.missing_count}</strong><small>{column.missing_percentage}%</small></td><td>{column.unique_count ?? 'Non calculé'}</td><td><div className="sample-values">{column.sample_values.map((value) => <span key={value}>{value}</span>)}</div></td></tr>)}</tbody></table></div> : <div className="empty-state"><Database /><h3>Profil indisponible</h3><p>Le profil apparaîtra lorsque la validation sera terminée.</p></div>}</section>
    </>
  )
}

function MissingValuesPanel({ datasetId, datasetStatus, onApplied, setActionError }) {
  const [analysis, setAnalysis] = useState(null)
  const [column, setColumn] = useState('')
  const [strategy, setStrategy] = useState('drop_rows')
  const [constantValue, setConstantValue] = useState('')
  const [busy, setBusy] = useState(false)

  async function analyze() {
    setBusy(true)
    setActionError('')
    try {
      const result = await api.missingValuesPreview(datasetId)
      setAnalysis(result)
      const firstMissing = result.columns.find((item) => item.missing_count > 0)
      setColumn(firstMissing?.name || '')
    } catch (error) { setActionError(error.message) }
    finally { setBusy(false) }
  }

  async function applyTreatment() {
    if (!window.confirm(`Créer une nouvelle version en traitant la colonne « ${column} » ? Le fichier original restera intact.`)) return
    setBusy(true)
    setActionError('')
    try {
      await api.applyMissingValues(datasetId, { column, strategy, value: constantValue })
      await onApplied()
      await analyze()
    } catch (error) { setActionError(error.message) }
    finally { setBusy(false) }
  }

  const selectedColumn = analysis?.columns.find((item) => item.name === column)
  const canApply = selectedColumn?.missing_count > 0 && !analysis?.truncated && !busy
  return <section className="panel missing-panel"><div className="panel-heading"><div><p className="eyebrow">Nettoyage · Valeurs manquantes</p><h2>Compléter ou retirer les données absentes</h2></div><button className="button secondary" onClick={analyze} disabled={busy || datasetStatus !== 'validated'}><Droplets /> {busy ? 'Traitement…' : analysis ? 'Analyser à nouveau' : 'Analyser'}</button></div>{!analysis ? <div className="cleaning-intro"><span className="cleaning-icon"><Droplets /></span><div><h3>Choisir une stratégie par colonne</h3><p>Suppression de lignes, constante, moyenne, médiane ou valeur la plus fréquente.</p></div><span className="read-only-badge"><ShieldCheck /> Prévisualisation</span></div> : <><div className="cleaning-summary"><article><span>Lignes analysées</span><strong>{analysis.analyzed_rows}</strong></article><article><span>Valeurs absentes</span><strong>{analysis.total_missing_values}</strong></article><article><span>Colonnes concernées</span><strong>{analysis.columns.filter((item) => item.missing_count > 0).length}</strong></article></div>{analysis.truncated && <div className="alert warning">Le fichier dépasse la limite synchrone : l’application est bloquée pour éviter un résultat partiel.</div>}{analysis.total_missing_values === 0 ? <div className="clean-result success"><CheckCircle2 /><div><strong>Aucune valeur manquante détectée</strong><p>Le périmètre analysé est complet.</p></div></div> : <div className="strategy-form"><label>Colonne<select value={column} onChange={(event) => setColumn(event.target.value)}>{analysis.columns.filter((item) => item.missing_count > 0).map((item) => <option key={item.name} value={item.name}>{item.name} · {item.missing_count} absente(s)</option>)}</select></label><label>Stratégie<select value={strategy} onChange={(event) => setStrategy(event.target.value)}><option value="drop_rows">Supprimer les lignes</option><option value="constant">Remplacer par une constante</option><option value="mode">Valeur la plus fréquente</option><option value="mean" disabled={!selectedColumn?.numeric}>Moyenne</option><option value="median" disabled={!selectedColumn?.numeric}>Médiane</option></select></label>{strategy === 'constant' && <label>Valeur de remplacement<input value={constantValue} onChange={(event) => setConstantValue(event.target.value)} placeholder="Ex. Inconnu" /></label>}<button className="button primary" onClick={applyTreatment} disabled={!canApply || (strategy === 'constant' && !constantValue)}><ShieldCheck /> Créer la version nettoyée</button></div>}</>}</section>
}

function TypeConversionPanel({ datasetId, datasetStatus, onApplied, setActionError }) {
  const [analysis, setAnalysis] = useState(null)
  const [column, setColumn] = useState('')
  const [targetType, setTargetType] = useState('string')
  const [busy, setBusy] = useState(false)

  async function analyze() {
    setBusy(true)
    setActionError('')
    try {
      const result = await api.typeConversionPreview(datasetId)
      setAnalysis(result)
      setColumn(result.columns[0]?.name || '')
    } catch (error) { setActionError(error.message) }
    finally { setBusy(false) }
  }

  async function applyConversion() {
    if (!window.confirm(`Créer une nouvelle version avec « ${column} » convertie en ${targetType} ?`)) return
    setBusy(true)
    setActionError('')
    try {
      await api.applyTypeConversion(datasetId, { column, target_type: targetType })
      await onApplied()
    } catch (error) { setActionError(error.message) }
    finally { setBusy(false) }
  }

  return <section className="panel"><div className="panel-heading"><div><p className="eyebrow">Nettoyage · Types</p><h2>Convertir une colonne</h2></div><button className="button secondary" onClick={analyze} disabled={busy || datasetStatus !== 'validated'}><Shuffle /> {busy ? 'Traitement…' : analysis ? 'Actualiser' : 'Préparer'}</button></div>{!analysis ? <div className="cleaning-intro"><span className="cleaning-icon"><Shuffle /></span><div><h3>Conversion stricte et contrôlée</h3><p>Les valeurs incompatibles sont signalées ; elles ne sont jamais remplacées silencieusement.</p></div><span className="read-only-badge"><ShieldCheck /> Confirmation requise</span></div> : <div className="strategy-form"><label>Colonne<select value={column} onChange={(event) => setColumn(event.target.value)}>{analysis.columns.map((item) => <option key={item.name} value={item.name}>{item.name} · {item.current_type}</option>)}</select></label><label>Type cible<select value={targetType} onChange={(event) => setTargetType(event.target.value)}><option value="integer">Entier</option><option value="float">Décimal</option><option value="string">Texte</option><option value="boolean">Booléen</option><option value="datetime">Date et heure</option></select></label><button className="button primary" onClick={applyConversion} disabled={!column || busy}><Shuffle /> Créer la version convertie</button></div>}</section>
}

function QualityAndExportPanel({ datasetId, datasetStatus, setActionError }) {
  const [report, setReport] = useState(null)
  const [loadingReport, setLoadingReport] = useState(false)

  async function loadReport() {
    setLoadingReport(true)
    setActionError('')
    try { setReport(await api.qualityReport(datasetId)) }
    catch (error) { setActionError(error.message) }
    finally { setLoadingReport(false) }
  }

  return <section className="panel"><div className="panel-heading"><div><p className="eyebrow">Qualité et livraison</p><h2>Rapport et exports</h2></div><div className="header-actions"><button className="button secondary" onClick={loadReport} disabled={loadingReport || datasetStatus !== 'validated'}><Gauge /> {loadingReport ? 'Calcul…' : 'Calculer la qualité'}</button><a className="button secondary" href={api.exportUrl(datasetId, 'csv')}><Download /> CSV</a><a className="button primary" href={api.exportUrl(datasetId, 'json')}><Download /> JSON</a></div></div>{report ? <><div className="quality-score"><div className="score-ring"><strong>{Math.round(report.overall_score)}</strong><span>/100</span></div><div><h3>Score qualité global</h3><p>60 % complétude et 40 % unicité. Ce score est déterministe et explicable.</p>{report.truncated && <span className="status status-pending">Analyse partielle</span>}</div></div><div className="cleaning-summary"><article><span>Complétude</span><strong>{report.completeness_score}%</strong><small>{report.missing_values} valeur(s) absente(s)</small></article><article><span>Unicité</span><strong>{report.uniqueness_score}%</strong><small>{report.duplicate_rows} doublon(s)</small></article><article><span>Périmètre</span><strong>{report.analyzed_rows}</strong><small>{report.column_count} colonne(s)</small></article></div></> : <div className="cleaning-intro"><span className="cleaning-icon"><Gauge /></span><div><h3>Mesurer avant d’exporter</h3><p>Le rapport synthétise la complétude et l’unicité du dataset courant.</p></div></div>}</section>
}

function AIRecommendationPanel({ datasetId, datasetStatus, setActionError }) {
  const [history, setHistory] = useState([])
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api.aiRecommendationHistory(datasetId)
      .then(setHistory)
      .catch((error) => setActionError(error.message))
  }, [datasetId, setActionError])

  async function requestRecommendation(forceAi) {
    setBusy(true)
    setActionError('')
    try {
      const result = await api.aiRecommendation(datasetId, forceAi)
      setHistory((items) => [result, ...items])
    } catch (error) { setActionError(error.message) }
    finally { setBusy(false) }
  }

  const latest = history[0]
  const recommendation = latest?.recommendation
  return <section className="panel ai-panel"><div className="panel-heading"><div><p className="eyebrow">Assistant qualité</p><h2>Recommandation hybride</h2></div><div className="header-actions"><button className="button secondary" onClick={() => requestRecommendation(false)} disabled={busy || datasetStatus !== 'validated'}><ShieldCheck /> Moteur hybride</button><button className="button primary" onClick={() => requestRecommendation(true)} disabled={busy || datasetStatus !== 'validated'}><Sparkles /> {busy ? 'Analyse…' : 'Interroger Qwen'}</button></div></div>{recommendation ? <div className="ai-recommendation"><span className="ai-mark"><Bot /></span><div className="ai-copy"><div className="ai-meta"><span className="status status-validated">{latest.engine_label}</span>{latest.model_name && <span>{latest.model_name}</span>}<span>Confiance {Math.round(recommendation.confidence * 100)} %</span></div><h3>{recommendation.action} · {recommendation.target}</h3><p>{recommendation.explanation}</p><div className="ai-guard"><ShieldCheck /> Recommandation seulement — confirmation humaine obligatoire avant transformation.</div></div></div> : <div className="cleaning-intro"><span className="cleaning-icon"><Bot /></span><div><h3>Règles sûres, puis Qwen pour les cas ambigus</h3><p>L’assistant analyse le profil mais ne modifie jamais les données automatiquement.</p></div><span className="read-only-badge"><ShieldCheck /> Sans application automatique</span></div>}{history.length > 1 && <div className="ai-history"><History /> {history.length} recommandations journalisées pour ce dataset</div>}</section>
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
