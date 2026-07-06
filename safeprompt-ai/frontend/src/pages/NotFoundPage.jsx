import { Link } from 'react-router-dom'
import { FiAlertCircle, FiArrowLeft } from 'react-icons/fi'

function NotFoundPage() {
  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <div className="w-full max-w-md space-y-4 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-risk-critical/10 text-risk-critical">
          <FiAlertCircle className="h-7 w-7" />
        </div>
        <h1 className="text-4xl font-extrabold text-slate-900 dark:text-white">404</h1>
        <p className="text-slate-600 dark:text-slate-300">
          The page you&apos;re looking for doesn&apos;t exist or has moved.
        </p>
        <Link to="/" className="btn-primary inline-flex">
          <FiArrowLeft className="h-4 w-4" />
          Back to Home
        </Link>
      </div>
    </div>
  )
}

export default NotFoundPage
