import { Navigate, Route, Routes } from 'react-router-dom'

import { AuthProvider } from './auth/AuthContext'
import { ProtectedRoute, RoleRoute } from './auth/guards'
import { DashboardLayout } from './layout/DashboardLayout'
import { getMenuLeaves } from './menu/menu'
import { DashboardPage } from './pages/DashboardPage'
import { ForbiddenPage } from './pages/ForbiddenPage'
import { LoginPage } from './pages/LoginPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { SectionPage } from './pages/SectionPage'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          {getMenuLeaves().map((item) => (
            <Route
              key={item.id}
              path={item.path?.replace(/^\//, '')}
              element={
                <RoleRoute>
                  {item.id === 'dashboard' ? (
                    <DashboardPage />
                  ) : (
                    <SectionPage item={item} />
                  )}
                </RoleRoute>
              }
            />
          ))}
          <Route path="403" element={<ForbiddenPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}