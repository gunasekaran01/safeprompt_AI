import { useCallback, useEffect, useState } from 'react'
import { FiAlertTriangle, FiRefreshCw } from 'react-icons/fi'
import StatsGrid from '../components/Dashboard/StatsGrid.jsx'
import RecentActivityTable from '../components/Dashboard/RecentActivityTable.jsx'
import DashboardCharts from '../components/Dashboard/DashboardCharts.jsx'
import { getDashboardStats, getRecentActivity, getDashboardCharts } from '../services/dashboardService.js'

/**
 * Dashboard page. Loads aggregate stats and recent activity from
 * dashboardService (currently mock data shaped like the real future API
 * response), with loading skeletons and error handling so the page
 * behaves correctly once it's wired to the live backend in later
 * milestones.
 */
function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [activity, setActivity] = useState([])
  const [charts, setCharts] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [error, setError] = useState(null)

  const loadDashboardData = useCallback(async ({ isRefresh = false } = {}) => {
    if (isRefresh) {
      setIsRefreshing(true)
    } else {
      setIsLoading(true)
    }
    setError(null)

    try {
      const [statsResponse, activityResponse, chartsResponse] = await Promise.all([
        getDashboardStats(),
        getRecentActivity(8),
        getDashboardCharts(14),
      ])
      setStats(statsResponse)
      setActivity(activityResponse)
      setCharts(chartsResponse)
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      setError('Something went wrong while loading the dashboard. Please try again.')
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }, [])

  useEffect(() => {
    loadDashboardData()
  }, [loadDashboardData])

  return (
    <div className="mx-auto max-w-7xl space-y-6 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Dashboard</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            An overview of prompt safety analyses across your account.
          </p>
        </div>
        <button
          type="button"
          onClick={() => loadDashboardData({ isRefresh: true })}
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
            onClick={() => loadDashboardData()}
            className="shrink-0 font-semibold underline underline-offset-2"
          >
            Retry
          </button>
        </div>
      )}

      <StatsGrid stats={stats} isLoading={isLoading} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RecentActivityTable activity={activity} isLoading={isLoading} />
        </div>
        <DashboardCharts charts={charts} isLoading={isLoading} />
      </div>
    </div>
  )
}

export default DashboardPage
