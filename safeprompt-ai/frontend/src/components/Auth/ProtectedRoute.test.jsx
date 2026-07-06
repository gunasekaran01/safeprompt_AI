import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import ProtectedRoute from './ProtectedRoute.jsx'
import { useAuth } from '../../context/AuthContext.jsx'

vi.mock('../../context/AuthContext.jsx', () => ({
  useAuth: vi.fn(),
}))

function renderProtectedRoute(initialPath = '/dashboard') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<div>Dashboard content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  )
}

describe('ProtectedRoute', () => {
  it('shows a loading spinner while the session is still being restored', () => {
    useAuth.mockReturnValue({ isAuthenticated: false, isLoading: true })
    renderProtectedRoute()
    expect(screen.queryByText('Dashboard content')).not.toBeInTheDocument()
    expect(screen.queryByText('Login page')).not.toBeInTheDocument()
  })

  it('redirects to /login when there is no session', () => {
    useAuth.mockReturnValue({ isAuthenticated: false, isLoading: false })
    renderProtectedRoute()
    expect(screen.getByText('Login page')).toBeInTheDocument()
  })

  it('renders the protected content when authenticated', () => {
    useAuth.mockReturnValue({ isAuthenticated: true, isLoading: false })
    renderProtectedRoute()
    expect(screen.getByText('Dashboard content')).toBeInTheDocument()
  })
})
