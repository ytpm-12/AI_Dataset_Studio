import { FolderKanban, Plus, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { api } from '../api/client'
import EmptyState from '../components/EmptyState'
import PageHeader from '../components/PageHeader'

export default function ProjectsPage() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [values, setValues] = useState({ name: '', description: '' })
  const [error, setError] = useState('')

  useEffect(() => {
    api.projects()
      .then((payload) => setProjects(payload.results))
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false))
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    try {
      const project = await api.createProject(values)
      setProjects((current) => [project, ...current])
      setValues({ name: '', description: '' })
      setShowForm(false)
    } catch (requestError) { setError(requestError.message) }
  }

  return (
    <>
      <PageHeader eyebrow="Organisation" title="Projets" description="Regroupez les imports qui partagent un même objectif métier." actions={<button className="button primary" onClick={() => setShowForm(true)}><Plus /> Nouveau projet</button>} />
      {error && <div className="alert error">{error}</div>}
      {showForm && <section className="panel form-panel"><div className="panel-heading"><div><p className="eyebrow">Nouveau</p><h2>Créer un projet</h2></div><button className="icon-button" onClick={() => setShowForm(false)} aria-label="Fermer"><X /></button></div><form className="inline-form" onSubmit={handleSubmit}><label>Nom<input required autoFocus value={values.name} onChange={(event) => setValues({ ...values, name: event.target.value })} placeholder="Ex. Données clients" /></label><label className="grow">Description<textarea rows="2" value={values.description} onChange={(event) => setValues({ ...values, description: event.target.value })} placeholder="Objectif et périmètre du projet" /></label><button className="button primary" type="submit">Créer</button></form></section>}
      {loading ? <div className="center-state"><span className="spinner" />Chargement des projets</div> : projects.length ? <section className="project-grid">{projects.map((project) => <article className="project-card" key={project.id}><div className="project-symbol"><FolderKanban /></div><div><h2>{project.name}</h2><p>{project.description || 'Aucune description renseignée.'}</p></div><footer><span>{project.uploaded_file_count} dataset{project.uploaded_file_count > 1 ? 's' : ''}</span><Link to="/datasets">Ouvrir</Link></footer></article>)}</section> : <section className="panel"><EmptyState icon={FolderKanban} title="Aucun projet" description="Créez un projet avant votre premier import." action={<button className="button primary" onClick={() => setShowForm(true)}><Plus /> Créer un projet</button>} /></section>}
    </>
  )
}
