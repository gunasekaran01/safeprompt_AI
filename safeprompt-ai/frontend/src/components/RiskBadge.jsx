import { getRiskLevelConfig } from '../utils/riskLevels.js'

/**
 * Colored pill showing a risk level (Safe, Low Risk, Medium Risk, High
 * Risk, Critical) with a matching icon. Reused wherever an analysis
 * result needs to display its risk classification.
 */
function RiskBadge({ riskLevel, size = 'md' }) {
  const config = getRiskLevelConfig(riskLevel)
  const Icon = config.icon

  const sizeClasses =
    size === 'sm' ? 'text-[11px] px-2 py-0.5 gap-1' : 'text-xs px-2.5 py-1 gap-1.5'

  return (
    <span
      className={`inline-flex items-center rounded-full font-semibold ${config.bgClass} ${config.textClass} ${sizeClasses}`}
    >
      <Icon className={size === 'sm' ? 'h-3 w-3' : 'h-3.5 w-3.5'} />
      {config.label}
    </span>
  )
}

export default RiskBadge
