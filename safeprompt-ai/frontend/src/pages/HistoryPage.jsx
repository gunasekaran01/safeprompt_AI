import { useCallback, useEffect, useState } from 'react'
import { FiAlertTriangle, FiChevronLeft, FiChevronRight, FiClock } from 'react-icons/fi'
import HistoryFilters from '../components/History/HistoryFilters.jsx'
import HistoryTable from '../components/History/HistoryTable.jsx'
import { deleteHistoryItem, getHistory } from '../services/historyService.js'

const PAGE_SIZE = 10
const SEARCH_DEBOUNCE_MS = 400

function HistoryPage() {
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [riskLevel, setRiskLevel] = useState('')
  const [offset, setOffset] = useState(0)

  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  // Debounce search input so we don't fire a request per keystroke.
  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setDebouncedSearch(search)
      setOffset(0)
    }, SEARCH_DEBOUNCE_MS)
    return () => window.clearTimeout(timeout)
  }, [search])

  // Reset to page 1 whenever the risk level filter changes.
  useEffect(() => {
    setOffset(0)
  }, [riskLevel])

  const loadHistory = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await getHistory({
        search: debouncedSearch,
        riskLevel,
        limit: PAGE_SIZE,
        offset,
      })
      setItems(response.items)
      setTotal(response.total)
    } catch (err) {
      setError(err.message || 'Failed to load history.')
    } finally {
      setIsLoading(false)
    }
  }, [debouncedSearch, riskLevel, offset])

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  const handleDelete = async (id) => {
    try {
      await deleteHistoryItem(id)
      await loadHistory()
    } catch (err) {
      setError(err.message || 'Failed to delete this analysis.')
    }
  }

  const currentPage = Math.floor(offset / PAGE_SIZE) + 1
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div className="mx-auto max-w-5xl space-y-6 px-4 py-10 sm:px-6 lg:px-8">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold text-slate-900 dark:text-white">
          <FiClock className="h-6 w-6 text-brand-600" />
          Analysis History
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Search, filter, and manage your past prompt analyses.
        </p>
      </div>

      <div className="card space-y-4">
        <HistoryFilters
          search={search}
          onSearchChange={setSearch}
          riskLevel={riskLevel}
          onRiskLevelChange={setRiskLevel}
        />

        {error && (
          <div className="flex items-center gap-2 rounded-lg border border-risk-critical/30 bg-risk-critical/10 px-3 py-2 text-sm text-risk-critical">
            <FiAlertTriangle className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        <HistoryTable items={items} isLoading={isLoading} onDelete={handleDelete} />

        {!isLoading && total > 0 && (
          <div className="flex items-center justify-between border-t border-slate-100 pt-4 text-xs text-slate-500 dark:border-slate-700 dark:text-slate-400">
            <span>
              Showing {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total}
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setOffset((prev) => Math.max(0, prev - PAGE_SIZE))}
                disabled={currentPage <= 1}
                className="btn-secondary !px-2 !py-1"
                aria-label="Previous page"
              >
                <FiChevronLeft className="h-4 w-4" />
              </button>
              <span>
                Page {currentPage} of {totalPages}
              </span>
              <button
                type="button"
                onClick={() => setOffset((prev) => prev + PAGE_SIZE)}
                disabled={currentPage >= totalPages}
                className="btn-secondary !px-2 !py-1"
                aria-label="Next page"
              >
                <FiChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default HistoryPage
