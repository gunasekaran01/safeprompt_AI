import { FiAlertOctagon, FiAlertTriangle, FiCheckCircle, FiInfo, FiXOctagon } from 'react-icons/fi'

/**
 * Single source of truth mapping a risk level key to its display label,
 * Tailwind color tokens (defined in tailwind.config.js under `risk.*`),
 * and icon. Consumed by RiskBadge and the safety score gauge so every
 * page renders risk levels consistently.
 */
export const RISK_LEVELS = {
  safe: {
    key: 'safe',
    label: 'Safe',
    icon: FiCheckCircle,
    textClass: 'text-risk-safe',
    bgClass: 'bg-risk-safe/10',
    borderClass: 'border-risk-safe/30',
    barClass: 'bg-risk-safe',
    hexColor: '#22c55e',
    minScore: 90,
  },
  low: {
    key: 'low',
    label: 'Low Risk',
    icon: FiInfo,
    textClass: 'text-risk-low',
    bgClass: 'bg-risk-low/10',
    borderClass: 'border-risk-low/30',
    barClass: 'bg-risk-low',
    hexColor: '#84cc16',
    minScore: 75,
  },
  medium: {
    key: 'medium',
    label: 'Medium Risk',
    icon: FiAlertTriangle,
    textClass: 'text-risk-medium',
    bgClass: 'bg-risk-medium/10',
    borderClass: 'border-risk-medium/30',
    barClass: 'bg-risk-medium',
    hexColor: '#f59e0b',
    minScore: 50,
  },
  high: {
    key: 'high',
    label: 'High Risk',
    icon: FiAlertOctagon,
    textClass: 'text-risk-high',
    bgClass: 'bg-risk-high/10',
    borderClass: 'border-risk-high/30',
    barClass: 'bg-risk-high',
    hexColor: '#f97316',
    minScore: 25,
  },
  critical: {
    key: 'critical',
    label: 'Critical',
    icon: FiXOctagon,
    textClass: 'text-risk-critical',
    bgClass: 'bg-risk-critical/10',
    borderClass: 'border-risk-critical/30',
    barClass: 'bg-risk-critical',
    hexColor: '#ef4444',
    minScore: 0,
  },
}

export const RISK_LEVEL_ORDER = ['safe', 'low', 'medium', 'high', 'critical']

/**
 * Resolves a numeric 0-100 safety score to a risk level key.
 * Mirrors the thresholds defined in backend/app/core/config.py so the
 * frontend's display logic (used with mock data until Milestone 9 wires
 * up the real scoring engine) matches backend behavior.
 */
export function getRiskLevelFromScore(score) {
  if (score >= RISK_LEVELS.safe.minScore) return 'safe'
  if (score >= RISK_LEVELS.low.minScore) return 'low'
  if (score >= RISK_LEVELS.medium.minScore) return 'medium'
  if (score >= RISK_LEVELS.high.minScore) return 'high'
  return 'critical'
}

export function getRiskLevelConfig(riskLevelKey) {
  return RISK_LEVELS[riskLevelKey] ?? RISK_LEVELS.medium
}
