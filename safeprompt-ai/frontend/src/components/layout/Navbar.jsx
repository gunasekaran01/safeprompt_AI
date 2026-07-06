import { useEffect, useRef, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  FiChevronDown,
  FiLogIn,
  FiLogOut,
  FiMenu,
  FiMoon,
  FiSettings,
  FiShield,
  FiSun,
  FiUser,
  FiX,
} from 'react-icons/fi'
import { NAV_ITEMS } from '../../utils/navigation.js'
import { useTheme } from '../../utils/ThemeContext.jsx'
import { useAuth } from '../../utils/AuthContext.jsx'
import { APP_NAME } from '../../utils/constants.js'

/**
 * Avatar + display-name button that opens a dropdown with Settings,
 * Admin (only if isAdmin), and Sign Out — replaces the previous
 * always-visible "email chip + separate Sign Out button" layout.
 * Falls back to an initials/icon avatar and the account's email if no
 * profile name/avatar has been set yet (see AuthContext's `profile`,
 * populated from GET /api/profiles/me).
 */
function UserMenu({ onNavigate }) {
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef(null)
  const { user, profile, isAdmin, signOut } = useAuth()
  const navigate = useNavigate()

  const displayName = profile?.name || user?.user_metadata?.name || user?.email
  const avatarUrl = profile?.avatarUrl

  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  async function handleSignOut() {
    setIsOpen(false)
    onNavigate?.()
    await signOut()
    navigate('/')
  }

  function goTo(path) {
    setIsOpen(false)
    onNavigate?.()
    navigate(path)
  }

  return (
    <div className="relative" ref={menuRef}>
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-haspopup="menu"
        aria-expanded={isOpen}
        className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800"
      >
        <span className="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full bg-brand-100 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
          {avatarUrl ? (
            <img src={avatarUrl} alt="" className="h-full w-full object-cover" />
          ) : (
            <FiUser className="h-4 w-4" />
          )}
        </span>
        <span className="hidden max-w-[9rem] truncate sm:inline">{displayName}</span>
        <FiChevronDown className={`h-3.5 w-3.5 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div
          role="menu"
          className="absolute right-0 mt-2 w-56 overflow-hidden rounded-xl border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-surface-dark"
        >
          <div className="border-b border-slate-100 px-4 py-3 dark:border-slate-800">
            <p className="truncate text-sm font-semibold text-slate-900 dark:text-white">
              {displayName}
            </p>
            <p className="truncate text-xs text-slate-500 dark:text-slate-400">{user?.email}</p>
          </div>
          <button
            type="button"
            role="menuitem"
            onClick={() => goTo('/settings')}
            className="flex w-full items-center gap-2 px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            <FiSettings className="h-4 w-4" />
            Settings
          </button>
          {isAdmin && (
            <button
              type="button"
              role="menuitem"
              onClick={() => goTo('/admin')}
              className="flex w-full items-center gap-2 px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              <FiShield className="h-4 w-4" />
              Admin Dashboard
            </button>
          )}
          <button
            type="button"
            role="menuitem"
            onClick={handleSignOut}
            className="flex w-full items-center gap-2 px-4 py-2 text-sm text-risk-critical hover:bg-risk-critical/10"
          >
            <FiLogOut className="h-4 w-4" />
            Sign Out
          </button>
        </div>
      )}
    </div>
  )
}

function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const { isDarkMode, toggleTheme } = useTheme()
  const { isAuthenticated, isAdmin, user, signOut } = useAuth()
  const navigate = useNavigate()

  const closeMobileMenu = () => setIsMobileMenuOpen(false)

  const visibleNavItems = NAV_ITEMS.filter((item) => {
    if (item.requiresAdmin && !isAdmin) return false
    if (item.requiresAuth && !isAuthenticated) return false
    return true
  })

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
          <div className="hidden md:block">
            {isAuthenticated ? (
              <UserMenu />
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
