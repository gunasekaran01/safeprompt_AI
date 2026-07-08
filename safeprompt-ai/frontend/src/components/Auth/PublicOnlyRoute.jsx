import { FiLoader } from 'react-icons/fi'
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../utils/AuthContext.jsx'

/**
 * Mirror of ProtectedRoute.jsx: wraps routes (via <Outlet />) that only
 * make sense as a pre-login landing experience -- Home and About. Once
 * signed in, visiting "/" or "/about" redirects to /dashboard instead,
 * so the marketing/landing pages are never shown "after login"; they're
 * hidden from the navbar too (see utils/navigation.js's `hideWhenAuth`).
 */
function PublicOnlyRoute() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <FiLoader className="h-6 w-6 animate-spin text-brand-600" />
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}

export default PublicOnlyRoute
