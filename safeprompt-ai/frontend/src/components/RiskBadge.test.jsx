import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import RiskBadge from './RiskBadge.jsx'

describe('RiskBadge', () => {
  it('renders the label for a known risk level', () => {
    render(<RiskBadge riskLevel="critical" />)
    expect(screen.getByText('Critical')).toBeInTheDocument()
  })

  it('falls back to the medium-risk label for an unrecognized level', () => {
    render(<RiskBadge riskLevel="not-a-real-level" />)
    expect(screen.getByText('Medium Risk')).toBeInTheDocument()
  })

  it('applies smaller sizing classes when size="sm"', () => {
    const { container } = render(<RiskBadge riskLevel="safe" size="sm" />)
    expect(container.querySelector('span')).toHaveClass('text-[11px]')
  })

  it('defaults to the medium ("md") sizing classes', () => {
    const { container } = render(<RiskBadge riskLevel="safe" />)
    expect(container.querySelector('span')).toHaveClass('text-xs')
  })
})
