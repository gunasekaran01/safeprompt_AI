import { Outlet } from 'react-router-dom'
import Navbar from './Navbar.jsx'
import Footer from './Footer.jsx'

/**
 * Top-level layout rendered around every route. Keeps the navbar and
 * footer persistent across page transitions while <Outlet /> swaps in
 * the active route's page component.
 */
function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-surface-light text-slate-800 transition-colors duration-200 dark:bg-surface-dark dark:text-slate-100">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}

export default Layout
