import { FiClock, FiGrid, FiHome, FiInfo, FiSearch, FiSettings } from 'react-icons/fi'

/**
 * Single source of truth for top-level app navigation.
 * `end: true` mirrors React Router's NavLink `end` prop so the Home link
 * doesn't stay active on every nested route.
 */
export const NAV_ITEMS = [
  { label: 'Home', path: '/', icon: FiHome, end: true, requiresAuth: false },
  { label: 'Dashboard', path: '/dashboard', icon: FiGrid, requiresAuth: true },
  { label: 'Analyzer', path: '/analyzer', icon: FiSearch, requiresAuth: true },
  { label: 'History', path: '/history', icon: FiClock, requiresAuth: true },
  { label: 'About', path: '/about', icon: FiInfo, requiresAuth: false },
  { label: 'Settings', path: '/settings', icon: FiSettings, requiresAuth: true },
]

export default NAV_ITEMS
