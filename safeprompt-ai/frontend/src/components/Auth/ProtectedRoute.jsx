import { FiLoader } from 'react-icons/fi'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../utils/AuthContext.jsx'

/**
 * Wraps a set of routes (via <Outlet />) so they're only reachable when
 * signed in. Shows a loading spinner while the initial session check is
 * in flight, then redirects to /login (preserving the attempted location
 * so LoginPage can send the user back where they were headed).
 */
function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <FiLoader className="h-6 w-6 animate-spin text-brand-600" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}

export default ProtectedRoute
