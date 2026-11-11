import { ArrowLeft, ArrowRight } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import useAuth from '../auth/useAuth'
import Brand from '../components/Brand'

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [values, setValues] = useState({ username: '', email: '', password: '', password_confirm: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function update(field, value) { setValues((current) => ({ ...current, [field]: value })) }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await register(values)
      navigate('/')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-layout">
      <section className="auth-story compact-story"><Brand /><div className="auth-statement"><p className="eyebrow light">Nouveau workspace</p><h1>Commencez par votre premier projet.</h1><p>Un compte suffit pour organiser les fichiers, profils et traitements de votre équipe.</p></div></section>
      <section className="auth-panel">
        <form className="auth-form" onSubmit={handleSubmit}>
          <Link className="back-link" to="/login"><ArrowLeft /> Retour</Link>
          <div><p className="eyebrow">Créer un compte</p><h2>Inscription</h2></div>
          {error && <div className="alert error" role="alert">{error}</div>}
          <label>Nom d’utilisateur<input autoComplete="username" required value={values.username} onChange={(event) => update('username', event.target.value)} /></label>
          <label>Adresse e-mail<input type="email" autoComplete="email" required value={values.email} onChange={(event) => update('email', event.target.value)} /></label>
          <div className="field-grid">
            <label>Mot de passe<input type="password" autoComplete="new-password" required value={values.password} onChange={(event) => update('password', event.target.value)} /></label>
            <label>Confirmation<input type="password" autoComplete="new-password" required value={values.password_confirm} onChange={(event) => update('password_confirm', event.target.value)} /></label>
          </div>
          <button className="button primary full" disabled={submitting}>{submitting ? 'Création…' : <>Créer le compte <ArrowRight /></>}</button>
        </form>
      </section>
    </div>
  )
}
