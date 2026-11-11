import { Navigate, Outlet, Route, Routes } from 'react-router-dom'

import useAuth from './auth/useAuth'
import AppShell from './components/AppShell'
import DashboardPage from './pages/DashboardPage'
import DatasetDetailPage from './pages/DatasetDetailPage'
import LoginPage from './pages/LoginPage'
import ProjectsPage from './pages/ProjectsPage'
import RegisterPage from './pages/RegisterPage'
import UploadsPage from './pages/UploadsPage'

function ProtectedLayout() {
  const { loading, user } = useAuth()
  if (loading) return <div className="center-state"><span className="spinner" />Chargement de l’espace de travail</div>
  if (!user) return <Navigate to="/login" replace />
  return <AppShell><Outlet /></AppShell>
}

function PublicOnly({ children }) {
  const { loading, user } = useAuth()
  if (loading) return <div className="center-state"><span className="spinner" />Chargement</div>
  return user ? <Navigate to="/" replace /> : children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicOnly><LoginPage /></PublicOnly>} />
      <Route path="/register" element={<PublicOnly><RegisterPage /></PublicOnly>} />
      <Route element={<ProtectedLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="projects" element={<ProjectsPage />} />
        <Route path="datasets" element={<UploadsPage />} />
        <Route path="datasets/:datasetId" element={<DatasetDetailPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
