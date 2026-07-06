import { getRiskLevelConfig } from '../../utils/riskLevels.js'
import { formatScore } from '../../utils/formatters.js'

const RADIUS = 54
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

/**
 * Circular 0-100 safety score gauge. Color follows the same risk-level
 * palette used by RiskBadge (utils/riskLevels.js) so the gauge, badge,
 * and reasoning panel always agree visually.
 */
function ScoreGauge({ score, riskLevel }) {
  const config = getRiskLevelConfig(riskLevel)
  const clamped = Math.max(0, Math.min(100, score))
  const offset = CIRCUMFERENCE - (clamped / 100) * CIRCUMFERENCE

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative h-36 w-36">
        <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90">
          <circle
            cx="60"
            cy="60"
            r={RADIUS}
            fill="none"
            strokeWidth="10"
            className="stroke-slate-100 dark:stroke-slate-700"
          />
          <circle
            cx="60"
            cy="60"
            r={RADIUS}
            fill="none"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={offset}
            className={`${config.textClass} transition-[stroke-dashoffset] duration-700 ease-out`}
            stroke="currentColor"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-extrabold text-slate-900 dark:text-white">
            {formatScore(clamped)}
          </span>
          <span className="text-[11px] font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
            / 100
          </span>
        </div>
      </div>
    </div>
  )
}

export default ScoreGauge
