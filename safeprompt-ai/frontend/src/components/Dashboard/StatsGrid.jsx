import {
  FiActivity,
  FiAlertOctagon,
  FiCheckCircle,
  FiShieldOff,
  FiTrendingUp,
  FiXCircle,
} from 'react-icons/fi'
import StatCard from './StatCard.jsx'
import { formatCount, formatScore } from '../../utils/formatters.js'

const SKELETON_COUNT = 6

function StatsGrid({ stats, isLoading }) {
  if (isLoading || !stats) {
    return (
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        {Array.from({ length: SKELETON_COUNT }).map((_, index) => (
          // eslint-disable-next-line react/no-array-index-key
          <StatCard key={index} isLoading />
        ))}
      </div>
    )
  }

  const cards = [
    {
      icon: FiActivity,
      label: 'Total Analyses',
      value: formatCount(stats.totalAnalyses),
      accentClassName: 'bg-brand-600',
    },
    {
      icon: FiCheckCircle,
      label: 'Safe Prompts',
      value: formatCount(stats.safePrompts),
      accentClassName: 'bg-risk-safe',
    },
    {
      icon: FiXCircle,
      label: 'Unsafe Prompts',
      value: formatCount(stats.unsafePrompts),
      accentClassName: 'bg-risk-critical',
    },
    {
      icon: FiShieldOff,
      label: 'Injection Attempts',
      value: formatCount(stats.injectionAttempts),
      accentClassName: 'bg-risk-high',
    },
    {
      icon: FiAlertOctagon,
      label: 'Toxic Prompts',
      value: formatCount(stats.toxicPrompts),
      accentClassName: 'bg-risk-medium',
    },
    {
      icon: FiTrendingUp,
      label: 'Avg. Safety Score',
      value: formatScore(stats.averageSafetyScore),
      accentClassName: 'bg-brand-500',
    },
  ]

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
      {cards.map((card) => (
        <StatCard key={card.label} {...card} />
      ))}
    </div>
  )
}

export default StatsGrid
