import { Link } from 'react-router-dom'
import { FiShield } from 'react-icons/fi'

/**
 * Centered card shell shared by Login, Register, Forgot Password, and
 * Reset Password pages, so they all look consistent without duplicating
 * the header/logo markup.
 */
function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4 py-12">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <Link to="/" className="inline-flex items-center justify-center">
            <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-600 text-white shadow-card">
              <FiShield className="h-6 w-6" />
            </span>
          </Link>
          <h1 className="mt-4 text-2xl font-bold text-slate-900 dark:text-white">{title}</h1>
          {subtitle && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>}
        </div>

        <div className="card">{children}</div>
      </div>
    </div>
  )
}

export default AuthLayout
