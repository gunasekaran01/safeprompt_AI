import { Link } from 'react-router-dom'
import { FiArrowRight, FiInbox } from 'react-icons/fi'
import RiskBadge from '../RiskBadge.jsx'
import { formatRelativeTime, formatScore, truncateText } from '../../utils/formatters.js'

function RecentActivitySkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, index) => (
        // eslint-disable-next-line react/no-array-index-key
        <div key={index} className="flex animate-pulse items-center gap-4 py-2">
          <div className="h-4 flex-1 rounded bg-slate-200 dark:bg-slate-700" />
          <div className="h-4 w-16 rounded bg-slate-200 dark:bg-slate-700" />
          <div className="h-5 w-20 rounded-full bg-slate-200 dark:bg-slate-700" />
        </div>
      ))}
    </div>
  )
}

function RecentActivityTable({ activity, isLoading }) {
  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-900 dark:text-white">Recent Activity</h2>
        <Link
          to="/history"
          className="flex items-center gap-1 text-xs font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
        >
          View Full History <FiArrowRight className="h-3 w-3" />
        </Link>
      </div>

      {isLoading ? (
        <RecentActivitySkeleton />
      ) : activity.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-10 text-center text-slate-400">
          <FiInbox className="h-8 w-8" />
          <p className="text-sm">No analyses yet. Try the Analyzer to get started.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-xs uppercase tracking-wide text-slate-400 dark:border-slate-700">
                <th className="pb-2 font-medium">Prompt</th>
                <th className="pb-2 font-medium">Time</th>
                <th className="pb-2 pr-2 text-right font-medium">Score</th>
                <th className="pb-2 pl-4 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {activity.map((item) => (
                <tr key={item.id} className="text-slate-700 dark:text-slate-300">
                  <td className="max-w-xs py-3 pr-4 text-sm">{truncateText(item.prompt, 64)}</td>
                  <td className="whitespace-nowrap py-3 pr-4 text-xs text-slate-400">
                    {formatRelativeTime(item.createdAt)}
                  </td>
                  <td className="whitespace-nowrap py-3 pr-2 text-right text-sm font-semibold">
                    {formatScore(item.safetyScore)}
                  </td>
                  <td className="whitespace-nowrap py-3 pl-4">
                    <RiskBadge riskLevel={item.riskLevel} size="sm" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default RecentActivityTable
