import { useCallback, useEffect, useState } from 'react'
import {
  FiActivity,
  FiAlertTriangle,
  FiCheckCircle,
  FiFileText,
  FiRefreshCw,
  FiShield,
  FiShieldOff,
  FiTrash2,
  FiTrendingUp,
  FiUsers,
  FiXCircle,
} from 'react-icons/fi'
import StatCard from '../components/Dashboard/StatCard.jsx'
import { formatCount, formatScore } from '../utils/formatters.js'
import { getAdminOverview, getAdminUsers, deleteAdminUser } from '../services/adminService.js'
import { useAuth } from '../context/AuthContext.jsx'

/**
 * Admin dashboard — platform-wide visibility for the SafePrompt AI admin
 * account (see utils/constants.js:ADMIN_EMAIL). Reachable only via
 * <AdminRoute> (components/Auth/AdminRoute.jsx), and every request is
 * independently re-authorized server-side regardless of how this page
 * was reached (app.api.deps.require_admin).
 *
 * Two sections: platform-wide stat cards (reusing Dashboard's StatCard),
 * and a table of every user with a delete action.
 */
function AdminPage() {
  const { user: currentUser } = useAuth()

  const [overview, setOverview] = useState(null)
  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [error, setError] = useState(null)

  const [confirmingUserId, setConfirmingUserId] = useState(null)
  const [deletingUserId, setDeletingUserId] = useState(null)
  const [deleteError, setDeleteError] = useState(null)

  const loadAdminData = useCallback(async ({ isRefresh = false } = {}) => {
    if (isRefresh) {
      setIsRefreshing(true)
    } else {
      setIsLoading(true)
    }
    setError(null)

    try {
      const [overviewResponse, usersResponse] = await Promise.all([
        getAdminOverview(),
        getAdminUsers(),
      ])
      setOverview(overviewResponse)
      setUsers(usersResponse.users)
    } catch (err) {
      setError(err.message || 'Something went wrong while loading the admin dashboard.')
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }, [])

  useEffect(() => {
    loadAdminData()
  }, [loadAdminData])

  async function handleDelete(userId) {
    if (confirmingUserId !== userId) {
      setConfirmingUserId(userId)
      return
    }

    setDeleteError(null)
    setDeletingUserId(userId)
    try {
      await deleteAdminUser(userId)
      setUsers((prev) => prev.filter((user) => user.id !== userId))
      setOverview((prev) => (prev ? { ...prev, totalUsers: prev.totalUsers - 1 } : prev))
    } catch (err) {
      setDeleteError(err.message || 'Failed to delete this user.')
    } finally {
      setDeletingUserId(null)
      setConfirmingUserId(null)
    }
  }

  const statCards = overview
    ? [
        { icon: FiUsers, label: 'Total Users', value: formatCount(overview.totalUsers), accentClassName: 'bg-brand-600' },
        { icon: FiActivity, label: 'Total Analyses', value: formatCount(overview.totalAnalyses), accentClassName: 'bg-brand-500' },
        { icon: FiFileText, label: 'Reports Generated', value: formatCount(overview.totalReports), accentClassName: 'bg-slate-500' },
        { icon: FiCheckCircle, label: 'Safe Prompts', value: formatCount(overview.safePrompts), accentClassName: 'bg-risk-safe' },
        { icon: FiXCircle, label: 'Unsafe Prompts', value: formatCount(overview.unsafePrompts), accentClassName: 'bg-risk-critical' },
        { icon: FiShieldOff, label: 'Injection Attempts', value: formatCount(overview.injectionAttempts), accentClassName: 'bg-risk-high' },
        { icon: FiAlertTriangle, label: 'Toxic Prompts', value: formatCount(overview.toxicPrompts), accentClassName: 'bg-risk-medium' },
        { icon: FiTrendingUp, label: 'Avg. Safety Score', value: formatScore(overview.averageSafetyScore), accentClassName: 'bg-brand-700' },
      ]
    : []

  return (
    <div className="mx-auto max-w-7xl space-y-6 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 text-white">
            <FiShield className="h-5 w-5" />
          </span>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Admin Dashboard</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Platform-wide activity across every SafePrompt AI user.
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => loadAdminData({ isRefresh: true })}
          disabled={isLoading || isRefreshing}
          className="btn-secondary self-start sm:self-auto"
        >
          <FiRefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="flex items-center justify-between gap-4 rounded-lg border border-risk-critical/30 bg-risk-critical/10 px-4 py-3 text-sm text-risk-critical">
          <div className="flex items-center gap-2">
            <FiAlertTriangle className="h-4 w-4 shrink-0" />
            {error}
          </div>
          <button
            type="button"
            onClick={() => loadAdminData()}
            className="shrink-0 font-semibold underline underline-offset-2"
          >
            Retry
          </button>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-4">
        {(isLoading ? Array.from({ length: 8 }) : statCards).map((card, index) =>
          isLoading ? (
            // eslint-disable-next-line react/no-array-index-key
            <StatCard key={index} isLoading />
          ) : (
            <StatCard key={card.label} {...card} />
          )
        )}
      </div>

      <div className="card overflow-hidden p-0">
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-800">
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
            Users ({isLoading ? '…' : formatCount(users.length)})
          </h2>
        </div>

        {deleteError && (
          <div className="flex items-center gap-2 border-b border-risk-critical/30 bg-risk-critical/10 px-5 py-3 text-sm text-risk-critical">
            <FiAlertTriangle className="h-4 w-4 shrink-0" />
            {deleteError}
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
              <tr>
                <th className="px-5 py-3">User</th>
                <th className="px-5 py-3">Role</th>
                <th className="px-5 py-3">Joined</th>
                <th className="px-5 py-3">Analyses</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {isLoading &&
                Array.from({ length: 5 }).map((_, index) => (
                  // eslint-disable-next-line react/no-array-index-key
                  <tr key={index} className="animate-pulse">
                    <td className="px-5 py-4">
                      <div className="h-4 w-40 rounded bg-slate-200 dark:bg-slate-700" />
                    </td>
                    <td className="px-5 py-4">
                      <div className="h-4 w-16 rounded bg-slate-200 dark:bg-slate-700" />
                    </td>
                    <td className="px-5 py-4">
                      <div className="h-4 w-20 rounded bg-slate-200 dark:bg-slate-700" />
                    </td>
                    <td className="px-5 py-4">
                      <div className="h-4 w-10 rounded bg-slate-200 dark:bg-slate-700" />
                    </td>
                    <td className="px-5 py-4" />
                  </tr>
                ))}

              {!isLoading && users.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-5 py-10 text-center text-sm text-slate-500 dark:text-slate-400">
                    No users yet.
                  </td>
                </tr>
              )}

              {!isLoading &&
                users.map((user) => {
                  const isSelf = user.id === currentUser?.id
                  const isConfirming = confirmingUserId === user.id
                  const isDeleting = deletingUserId === user.id

                  return (
                    <tr key={user.id} className="text-slate-700 dark:text-slate-300">
                      <td className="px-5 py-4">
                        <p className="font-medium text-slate-900 dark:text-white">
                          {user.name || user.email}
                        </p>
                        {user.name && (
                          <p className="text-xs text-slate-500 dark:text-slate-400">{user.email}</p>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        {user.isAdmin ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
                            <FiShield className="h-3 w-3" />
                            Admin
                          </span>
                        ) : (
                          <span className="text-xs text-slate-500 dark:text-slate-400">User</span>
                        )}
                      </td>
                      <td className="px-5 py-4 text-xs text-slate-500 dark:text-slate-400">
                        {new Date(user.createdAt).toLocaleDateString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })}
                      </td>
                      <td className="px-5 py-4">{formatCount(user.analysesCount)}</td>
                      <td className="px-5 py-4 text-right">
                        {isSelf ? (
                          <span className="text-xs text-slate-400 dark:text-slate-500">You</span>
                        ) : (
                          <button
                            type="button"
                            onClick={() => handleDelete(user.id)}
                            onBlur={() => setConfirmingUserId(null)}
                            disabled={isDeleting}
                            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
                              isConfirming
                                ? 'bg-risk-critical text-white hover:bg-risk-critical/90'
                                : 'text-risk-critical hover:bg-risk-critical/10'
                            }`}
                          >
                            <FiTrash2 className="h-3.5 w-3.5" />
                            {isDeleting ? 'Deleting…' : isConfirming ? 'Confirm delete?' : 'Delete'}
                          </button>
                        )}
                      </td>
                    </tr>
                  )
                })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default AdminPage
