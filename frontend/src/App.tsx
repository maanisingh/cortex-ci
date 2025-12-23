import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/common/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Entities from './pages/Entities'
import EntityDetail from './pages/EntityDetail'
import Constraints from './pages/Constraints'
import ConstraintDetail from './pages/ConstraintDetail'
import Dependencies from './pages/Dependencies'
import Risks from './pages/Risks'
import Scenarios from './pages/Scenarios'
import ScenarioDetail from './pages/ScenarioDetail'
import AuditLog from './pages/AuditLog'
import AuditLogDetail from './pages/AuditLogDetail'
import Settings from './pages/Settings'
import UserManagement from './pages/UserManagement'
import Profile from './pages/Profile'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/entities" element={<Entities />} />
                <Route path="/entities/:id" element={<EntityDetail />} />
                <Route path="/constraints" element={<Constraints />} />
                <Route path="/constraints/:id" element={<ConstraintDetail />} />
                <Route path="/dependencies" element={<Dependencies />} />
                <Route path="/risks" element={<Risks />} />
                <Route path="/scenarios" element={<Scenarios />} />
                <Route path="/scenarios/:id" element={<ScenarioDetail />} />
                <Route path="/audit" element={<AuditLog />} />
                <Route path="/audit/:id" element={<AuditLogDetail />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/admin/users" element={<UserManagement />} />
                <Route path="/profile" element={<Profile />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App
