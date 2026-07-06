import { Link } from 'react-router-dom'

/**
 * Catch-all 404 page for unmatched routes.
 */
function NotFound() {
  return (
    <div className="card mx-auto max-w-xl space-y-4 text-center">
      <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white">404</h1>
      <p className="text-sm text-slate-600 dark:text-slate-300">
        The page you&apos;re looking for doesn&apos;t exist.
      </p>
      <Link to="/" className="btn-primary mx-auto w-fit">
        Back to Home
      </Link>
    </div>
  )
}

export default NotFound
