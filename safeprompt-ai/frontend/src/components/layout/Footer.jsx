import { Link } from 'react-router-dom'
import { FiShield } from 'react-icons/fi'
import { APP_NAME, APP_DESCRIPTION } from '../../utils/constants.js'

function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-surface-dark">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-md bg-brand-600 text-white">
              <FiShield className="h-4 w-4" />
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-900 dark:text-white">{APP_NAME}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">{APP_DESCRIPTION}</p>
            </div>
          </div>

          <div className="flex items-center gap-6 text-sm text-slate-500 dark:text-slate-400">
            <Link to="/about" className="hover:text-brand-600 dark:hover:text-brand-400">
              About
            </Link>
            <Link to="/settings" className="hover:text-brand-600 dark:hover:text-brand-400">
              Settings
            </Link>
            <Link to="/analyzer" className="hover:text-brand-600 dark:hover:text-brand-400">
              Analyzer
            </Link>
          </div>
        </div>

        <div className="mt-6 border-t border-slate-100 pt-6 text-center text-xs text-slate-400 dark:border-slate-800 dark:text-slate-500">
          © {currentYear} {APP_NAME}. Built for AI safety research and education.
        </div>
      </div>
    </footer>
  )
}

export default Footer
