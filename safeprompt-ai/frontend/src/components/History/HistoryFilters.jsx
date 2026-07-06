import { FiSearch } from 'react-icons/fi'
import { RISK_LEVEL_ORDER, getRiskLevelConfig } from '../../utils/riskLevels.js'

function HistoryFilters({ search, onSearchChange, riskLevel, onRiskLevelChange }) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div className="relative flex-1">
        <FiSearch className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search prompts…"
          className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
        />
      </div>

      <select
        value={riskLevel}
        onChange={(event) => onRiskLevelChange(event.target.value)}
        className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
      >
        <option value="">All risk levels</option>
        {RISK_LEVEL_ORDER.map((key) => (
          <option key={key} value={key}>
            {getRiskLevelConfig(key).label}
          </option>
        ))}
      </select>
    </div>
  )
}

export default HistoryFilters
