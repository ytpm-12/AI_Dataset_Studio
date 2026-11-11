import { Database, FileJson, FileSpreadsheet, FileType2, Upload, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { api } from '../api/client'
import EmptyState from '../components/EmptyState'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

const formatIcons = { csv: FileSpreadsheet, json: FileJson, xml: FileType2 }

export default function UploadsPage() {
  const [projects, setProjects] = useState([])
  const [uploads, setUploads] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [file, setFile] = useState(null)
  const [values, setValues] = useState({ project: '', name: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    Promise.all([api.projects(), api.uploads()])
      .then(([projectPayload, uploadPayload]) => { setProjects(projectPayload.results); setUploads(uploadPayload.results) })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false))
  }, [])

  async function handleUpload(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    const formData = new FormData()
    formData.append('project', values.project)
    formData.append('name', values.name)
    formData.append('file', file)
    try {
      const created = await api.upload(formData)
      setUploads((current) => [created, ...current])
      setValues({ project: '', name: '' })
      setFile(null)
      setShowForm(false)
    } catch (requestError) { setError(requestError.message) }
    finally { setSubmitting(false) }
  }

  return (
    <>
      <PageHeader eyebrow="Données" title="Datasets" description="Importez vos sources et consultez leur état de validation." actions={<button className="button primary" onClick={() => setShowForm(true)} disabled={!projects.length}><Upload /> Importer</button>} />
      {error && <div className="alert error">{error}</div>}
      {!projects.length && !loading && <div className="alert warning">Créez d’abord un projet pour pouvoir importer un fichier. <Link to="/projects">Créer un projet</Link></div>}
      {showForm && <section className="panel form-panel"><div className="panel-heading"><div><p className="eyebrow">Nouvelle source</p><h2>Importer un dataset</h2></div><button className="icon-button" onClick={() => setShowForm(false)} aria-label="Fermer"><X /></button></div><form className="upload-form" onSubmit={handleUpload}><div className="field-grid"><label>Projet<select required value={values.project} onChange={(event) => setValues({ ...values, project: event.target.value })}><option value="">Sélectionner</option>{projects.map((project) => <option value={project.id} key={project.id}>{project.name}</option>)}</select></label><label>Nom du dataset<input value={values.name} onChange={(event) => setValues({ ...values, name: event.target.value })} placeholder="Utilise le nom du fichier si vide" /></label></div><label className="file-drop"><Upload /><strong>{file ? file.name : 'Choisir un fichier'}</strong><span>CSV, JSON ou XML · 50 Mo maximum</span><input type="file" required accept=".csv,.json,.xml" onChange={(event) => setFile(event.target.files[0])} /></label><div className="form-actions"><button className="button secondary" type="button" onClick={() => setShowForm(false)}>Annuler</button><button className="button primary" disabled={submitting || !file}>{submitting ? 'Import en cours…' : 'Lancer l’import'}</button></div></form></section>}
      <section className="panel">
        {loading ? <div className="loading-row"><span className="spinner" />Chargement des datasets</div> : uploads.length ? <div className="dataset-list">{uploads.map((upload) => { const Icon = formatIcons[upload.file_type] || Database; return <Link className="dataset-row" to={`/datasets/${upload.id}`} key={upload.id}><span className={`file-icon ${upload.file_type}`}><Icon /></span><span className="dataset-name"><strong>{upload.name}</strong><small>{upload.original_name}</small></span><span className="dataset-meta">{upload.file_type.toUpperCase()}</span><span className="dataset-meta">{formatBytes(upload.size)}</span><StatusBadge status={upload.status} /></Link> })}</div> : <EmptyState icon={Database} title="Aucun dataset" description="Les fichiers importés apparaîtront ici." action={projects.length ? <button className="button primary" onClick={() => setShowForm(true)}><Upload /> Importer</button> : null} />}
      </section>
    </>
  )
}

function formatBytes(bytes) { return bytes < 1024 ** 2 ? `${(bytes / 1024).toFixed(1)} Ko` : `${(bytes / 1024 ** 2).toFixed(1)} Mo` }
