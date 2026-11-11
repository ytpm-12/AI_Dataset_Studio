import { ArrowRight, CheckCircle2 } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import useAuth from '../auth/useAuth'
import Brand from '../components/Brand'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [values, setValues] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(values)
      navigate('/')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-layout">
      <section className="auth-story">
        <Brand />
        <div className="auth-statement">
          <p className="eyebrow light">Espace de préparation</p>
          <h1>Des données brutes à un dataset fiable.</h1>
          <p>Centralisez vos imports, contrôlez leur qualité et suivez chaque traitement dans un espace de travail commun.</p>
        </div>
        <ul className="auth-benefits">
          <li><CheckCircle2 /> Profilage CSV, JSON et XML</li>
          <li><CheckCircle2 /> Traitements suivis et auditables</li>
          <li><CheckCircle2 /> Données isolées par utilisateur</li>
        </ul>
      </section>
      <section className="auth-panel">
        <form className="auth-form" onSubmit={handleSubmit}>
          <div><p className="eyebrow">Bon retour</p><h2>Connexion</h2><p className="muted">Accédez à votre espace de travail.</p></div>
          {error && <div className="alert error" role="alert">{error}</div>}
          <label>Nom d’utilisateur<input autoComplete="username" required value={values.username} onChange={(event) => setValues({ ...values, username: event.target.value })} /></label>
          <label>Mot de passe<input type="password" autoComplete="current-password" required value={values.password} onChange={(event) => setValues({ ...values, password: event.target.value })} /></label>
          <button className="button primary full" disabled={submitting}>{submitting ? 'Connexion…' : <>Se connecter <ArrowRight /></>}</button>
          <p className="auth-switch">Pas encore de compte ? <Link to="/register">Créer un compte</Link></p>
        </form>
      </section>
    </div>
  )
}
