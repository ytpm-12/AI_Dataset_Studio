import { Database, FolderKanban, LayoutDashboard, LogOut, Upload } from 'lucide-react'
import { NavLink, useNavigate } from 'react-router-dom'

import useAuth from '../auth/useAuth'
import Brand from './Brand'

const links = [
  { to: '/', label: 'Vue d’ensemble', icon: LayoutDashboard, end: true },
  { to: '/projects', label: 'Projets', icon: FolderKanban },
  { to: '/datasets', label: 'Datasets', icon: Database },
]

export default function AppShell({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <aside className="rail">
        <Brand />
        <nav className="rail-nav" aria-label="Navigation principale">
          <span className="rail-label">Espace de travail</span>
          {links.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} className={({ isActive }) => `rail-link${isActive ? ' is-active' : ''}`}>
              <Icon aria-hidden="true" />
              <span>{label}</span>
            </NavLink>
          ))}
          <NavLink to="/datasets" className="rail-link rail-action">
            <Upload aria-hidden="true" />
            <span>Nouvel import</span>
          </NavLink>
        </nav>
        <div className="rail-account">
          <div className="avatar" aria-hidden="true">{user.username.slice(0, 2).toUpperCase()}</div>
          <div className="account-copy"><strong>{user.username}</strong><span>{user.email || 'Compte local'}</span></div>
          <button className="icon-button inverse" onClick={handleLogout} title="Se déconnecter" aria-label="Se déconnecter"><LogOut /></button>
        </div>
      </aside>
      <main className="workspace">{children}</main>
    </div>
  )
}
