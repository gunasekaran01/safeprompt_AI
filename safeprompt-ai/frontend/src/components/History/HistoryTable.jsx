import { useState } from 'react'
import { FiInbox, FiLoader, FiTrash2, FiX } from 'react-icons/fi'
import RiskBadge from '../RiskBadge.jsx'
import { formatRelativeTime, formatScore, truncateText } from '../../utils/formatters.js'

function HistoryTable({ items, isLoading, onDelete }) {
  const [pendingDeleteId, setPendingDeleteId] = useState(null)
  const [deletingId, setDeletingId] = useState(null)

  const handleConfirmDelete = async (id) => {
    setDeletingId(id)
    try {
      await onDelete(id)
    } finally {
      setDeletingId(null)
      setPendingDeleteId(null)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 6 }).map((_, index) => (
          // eslint-disable-next-line react/no-array-index-key
          <div key={index} className="flex animate-pulse items-center gap-4 py-3">
            <div className="h-4 flex-1 rounded bg-slate-200 dark:bg-slate-700" />
            <div className="h-4 w-20 rounded bg-slate-200 dark:bg-slate-700" />
            <div className="h-5 w-20 rounded-full bg-slate-200 dark:bg-slate-700" />
          </div>
        ))}
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-16 text-center text-slate-400">
        <FiInbox className="h-8 w-8" />
        <p className="text-sm">No analyses match your filters yet.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-slate-100 text-xs uppercase tracking-wide text-slate-400 dark:border-slate-700">
            <th className="pb-2 font-medium">Prompt</th>
            <th className="pb-2 font-medium">Time</th>
            <th className="pb-2 pr-2 text-right font-medium">Score</th>
            <th className="pb-2 pl-4 font-medium">Status</th>
            <th className="pb-2 pl-4 font-medium">
              <span className="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
          {items.map((item) => (
            <tr key={item.id} className="text-slate-700 dark:text-slate-300">
              <td className="max-w-xs py-3 pr-4 text-sm" title={item.prompt}>
                {truncateText(item.prompt, 70)}
              </td>
              <td className="whitespace-nowrap py-3 pr-4 text-xs text-slate-400">
                {formatRelativeTime(item.createdAt)}
              </td>
              <td className="whitespace-nowrap py-3 pr-2 text-right text-sm font-semibold">
                {formatScore(item.safetyScore)}
              </td>
              <td className="whitespace-nowrap py-3 pl-4">
                <RiskBadge riskLevel={item.riskLevel} size="sm" />
              </td>
              <td className="whitespace-nowrap py-3 pl-4 text-right">
                {pendingDeleteId === item.id ? (
                  <div className="flex items-center justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => handleConfirmDelete(item.id)}
                      disabled={deletingId === item.id}
                      className="text-xs font-semibold text-risk-critical hover:underline"
                    >
                      {deletingId === item.id ? (
                        <FiLoader className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        'Confirm'
                      )}
                    </button>
                    <button
                      type="button"
                      onClick={() => setPendingDeleteId(null)}
                      className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                      aria-label="Cancel delete"
                    >
                      <FiX className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => setPendingDeleteId(item.id)}
                    className="text-slate-400 hover:text-risk-critical"
                    aria-label="Delete analysis"
                  >
                    <FiTrash2 className="h-3.5 w-3.5" />
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default HistoryTable
