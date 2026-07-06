import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { FiLogIn, FiLogOut, FiMenu, FiMoon, FiShield, FiSun, FiUser, FiX } from 'react-icons/fi'
import { NAV_ITEMS } from '../../utils/navigation.js'
import { useTheme } from '../../utils/ThemeContext.jsx'
import { useAuth } from '../../utils/AuthContext.jsx'
import { APP_NAME } from '../../utils/constants.js'

function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const { isDarkMode, toggleTheme } = useTheme()
  const { isAuthenticated, user, signOut } = useAuth()
  const navigate = useNavigate()

  const closeMobileMenu = () => setIsMobileMenuOpen(false)

  const visibleNavItems = NAV_ITEMS.filter((item) => !item.requiresAuth || isAuthenticated)

  const linkClasses = ({ isActive }) =>
    `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
      isActive
        ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300'
        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white'
    }`

  const handleSignOut = async () => {
    closeMobileMenu()
    await signOut()
    navigate('/')
  }

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-surface-dark/90">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo / brand */}
        <NavLink to="/" className="flex items-center gap-2" onClick={closeMobileMenu}>
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-white">
            <FiShield className="h-5 w-5" />
          </span>
          <span className="text-lg font-extrabold tracking-tight text-slate-900 dark:text-white">
            {APP_NAME}
          </span>
        </NavLink>

        {/* Desktop nav links */}
        <div className="hidden items-center gap-1 md:flex">
          {visibleNavItems.map(({ label, path, icon: Icon, end }) => (
            <NavLink key={path} to={path} end={end} className={linkClasses}>
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </div>

        {/* Right-side actions */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={toggleTheme}
            aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            {isDarkMode ? <FiSun className="h-5 w-5" /> : <FiMoon className="h-5 w-5" />}
          </button>

          {/* Auth state — desktop */}
          <div className="hidden items-center gap-2 md:flex">
            {isAuthenticated ? (
              <>
                <span className="flex items-center gap-1.5 rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                  <FiUser className="h-3.5 w-3.5" />
                  {user?.email}
                </span>
                <button type="button" onClick={handleSignOut} className="btn-secondary !px-3 !py-1.5 text-xs">
                  <FiLogOut className="h-3.5 w-3.5" />
                  Sign Out
                </button>
              </>
            ) : (
              <NavLink to="/login" className="btn-primary !px-3 !py-1.5 text-xs">
                <FiLogIn className="h-3.5 w-3.5" />
                Sign In
              </NavLink>
            )}
          </div>

          <button
            type="button"
            onClick={() => setIsMobileMenuOpen((prev) => !prev)}
            aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={isMobileMenuOpen}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800 md:hidden"
          >
            {isMobileMenuOpen ? <FiX className="h-5 w-5" /> : <FiMenu className="h-5 w-5" />}
          </button>
        </div>
      </nav>

      {/* Mobile nav menu */}
      {isMobileMenuOpen && (
        <div className="border-t border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-surface-dark md:hidden">
          <div className="flex flex-col gap-1">
            {visibleNavItems.map(({ label, path, icon: Icon, end }) => (
              <NavLink key={path} to={path} end={end} className={linkClasses} onClick={closeMobileMenu}>
                <Icon className="h-4 w-4" />
                {label}
              </NavLink>
            ))}

            <div className="mt-2 border-t border-slate-100 pt-2 dark:border-slate-800">
              {isAuthenticated ? (
                <button
                  type="button"
                  onClick={handleSignOut}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-risk-critical hover:bg-risk-critical/10"
                >
                  <FiLogOut className="h-4 w-4" />
                  Sign Out ({user?.email})
                </button>
              ) : (
                <NavLink
                  to="/login"
                  onClick={closeMobileMenu}
                  className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-brand-600 hover:bg-brand-50 dark:text-brand-400 dark:hover:bg-brand-900/30"
                >
                  <FiLogIn className="h-4 w-4" />
                  Sign In
                </NavLink>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  )
}

export default Navbar
