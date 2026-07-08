import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout/Layout.jsx'
import ProtectedRoute from './components/Auth/ProtectedRoute.jsx'
import PublicOnlyRoute from './components/Auth/PublicOnlyRoute.jsx'
import AdminRoute from './components/Auth/AdminRoute.jsx'
import HomePage from './pages/HomePage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import AnalyzerPage from './pages/AnalyzerPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import AboutPage from './pages/AboutPage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'
import AdminPage from './pages/AdminPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import ForgotPasswordPage from './pages/ForgotPasswordPage.jsx'
import ResetPasswordPage from './pages/ResetPasswordPage.jsx'
import NotFoundPage from './pages/NotFoundPage.jsx'

/**
 * Top-level route table. All routes render inside the shared <Layout />
 * (navbar + footer). Home and About are the pre-login landing pages --
 * wrapped in <PublicOnlyRoute />, they redirect an already-signed-in
 * user straight to /dashboard, so they're never shown "after login"
 * (and utils/navigation.js hides their nav links once authenticated,
 * for the same reason). Dashboard, Analyzer, History, and Settings
 * require an authenticated session via <ProtectedRoute />; /admin
 * additionally requires isAdmin via <AdminRoute />. The auth pages
 * (login/register/forgot/reset) stay public/unrestricted. Unmatched
 * paths fall through to the 404 page.
 */
function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* Public landing pages -- redirect to /dashboard if already signed in */}
        <Route element={<PublicOnlyRoute />}>
          <Route index element={<HomePage />} />
          <Route path="about" element={<AboutPage />} />
        </Route>

        {/* Public routes */}
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="forgot-password" element={<ForgotPasswordPage />} />
        <Route path="reset-password" element={<ResetPasswordPage />} />

        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="analyzer" element={<AnalyzerPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* Admin-only route */}
        <Route element={<AdminRoute />}>
          <Route path="admin" element={<AdminPage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}

export default App
