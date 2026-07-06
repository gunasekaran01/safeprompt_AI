import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { FiLoader } from 'react-icons/fi'
import { useAuth } from '../../utils/AuthContext.jsx'

/**
 * Route guard for the admin dashboard (/admin — see App.jsx). Requires
 * both an authenticated session *and* isAdmin (fetched from GET
 * /api/auth/me by utils/AuthContext.jsx — computed server-side, never a
 * client-side email comparison). Mirrors ProtectedRoute.jsx's
 * loading/redirect pattern:
 * - Still restoring the session -> full-page spinner.
 * - Not logged in -> redirect to /login (remembering where they were
 *   headed, same as ProtectedRoute).
 * - Logged in but not an admin -> redirect to /dashboard rather than
 *   /login, since re-authenticating wouldn't change the outcome.
 *
 * This is a UI convenience only. Every /api/admin/... call is still
 * independently authorized server-side (app.api.deps.require_admin) —
 * this guard can never be the only thing standing between a non-admin
 * and admin data.
 */
function AdminRoute() {
  const { isAuthenticated, isAdmin, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <FiLoader className="h-6 w-6 animate-spin text-brand-600" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (!isAdmin) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}

export default AdminRoute
