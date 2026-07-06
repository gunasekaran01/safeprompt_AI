import { FiClock, FiGrid, FiHome, FiInfo, FiSearch, FiSettings, FiShield } from 'react-icons/fi'

/**
 * Single source of truth for top-level app navigation.
 * `end: true` mirrors React Router's NavLink `end` prop so the Home link
 * doesn't stay active on every nested route. `requiresAdmin` items are
 * additionally filtered out unless AuthContext's `isAdmin` is true (see
 * Navbar.jsx) — this is a UI convenience only, never the actual access
 * control (that's app.api.deps.require_admin, server-side).
 */
export const NAV_ITEMS = [
  { label: 'Home', path: '/', icon: FiHome, end: true, requiresAuth: false },
  { label: 'Dashboard', path: '/dashboard', icon: FiGrid, requiresAuth: true },
  { label: 'Analyzer', path: '/analyzer', icon: FiSearch, requiresAuth: true },
  { label: 'History', path: '/history', icon: FiClock, requiresAuth: true },
  { label: 'About', path: '/about', icon: FiInfo, requiresAuth: false },
  { label: 'Settings', path: '/settings', icon: FiSettings, requiresAuth: true },
  { label: 'Admin', path: '/admin', icon: FiShield, requiresAuth: true, requiresAdmin: true },
]

export default NAV_ITEMS
