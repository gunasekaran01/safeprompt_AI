import { describe, expect, it } from 'vitest'
import {
  RISK_LEVELS,
  RISK_LEVEL_ORDER,
  getRiskLevelConfig,
  getRiskLevelFromScore,
} from './riskLevels.js'

describe('getRiskLevelFromScore', () => {
  it('classifies boundary scores using the same thresholds as backend/app/core/config.py', () => {
    expect(getRiskLevelFromScore(100)).toBe('safe')
    expect(getRiskLevelFromScore(90)).toBe('safe')
    expect(getRiskLevelFromScore(89)).toBe('low')
    expect(getRiskLevelFromScore(75)).toBe('low')
    expect(getRiskLevelFromScore(74)).toBe('medium')
    expect(getRiskLevelFromScore(50)).toBe('medium')
    expect(getRiskLevelFromScore(49)).toBe('high')
    expect(getRiskLevelFromScore(25)).toBe('high')
    expect(getRiskLevelFromScore(24)).toBe('critical')
    expect(getRiskLevelFromScore(0)).toBe('critical')
  })
})

describe('getRiskLevelConfig', () => {
  it('returns the matching config for a known risk level', () => {
    expect(getRiskLevelConfig('safe')).toBe(RISK_LEVELS.safe)
    expect(getRiskLevelConfig('critical').label).toBe('Critical')
  })

  it('falls back to medium for an unknown/missing risk level rather than throwing', () => {
    expect(getRiskLevelConfig('not-a-real-level')).toBe(RISK_LEVELS.medium)
    expect(getRiskLevelConfig(undefined)).toBe(RISK_LEVELS.medium)
  })
})

describe('RISK_LEVEL_ORDER', () => {
  it('lists every key defined in RISK_LEVELS, worst to best matching the UI legend order', () => {
    expect(RISK_LEVEL_ORDER).toEqual(['safe', 'low', 'medium', 'high', 'critical'])
    expect(new Set(RISK_LEVEL_ORDER)).toEqual(new Set(Object.keys(RISK_LEVELS)))
  })
})
