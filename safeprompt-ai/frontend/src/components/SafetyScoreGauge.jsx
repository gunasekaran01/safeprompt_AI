import { getRiskLevelConfig, getRiskLevelFromScore } from '../utils/riskLevels.js'

/**
 * Circular progress gauge showing a 0-100 safety score, colored to match
 * the resolved risk level. Uses raw SVG + hex colors (rather than
 * Tailwind utility classes) because stroke-dasharray/stroke color need
 * literal values.
 */
function SafetyScoreGauge({ score, size = 160, strokeWidth = 14 }) {
  const clampedScore = Math.max(0, Math.min(100, score))
  const riskLevelKey = getRiskLevelFromScore(clampedScore)
  const config = getRiskLevelConfig(riskLevelKey)

  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const dashOffset = circumference * (1 - clampedScore / 100)

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          className="stroke-slate-100 dark:stroke-slate-700"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          stroke={config.hexColor}
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-extrabold text-slate-900 dark:text-white">
          {Math.round(clampedScore)}
        </span>
        <span className="text-xs font-medium text-slate-400">/ 100</span>
      </div>
    </div>
  )
}

export default SafetyScoreGauge
