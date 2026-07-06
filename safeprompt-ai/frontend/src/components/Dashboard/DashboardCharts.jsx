import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'
import { Bar, Doughnut, Line } from 'react-chartjs-2'
import { FiBarChart2 } from 'react-icons/fi'
import { RISK_LEVEL_ORDER, getRiskLevelConfig } from '../../utils/riskLevels.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Filler,
  Tooltip,
  Legend
)

const AXIS_COLOR = 'rgba(148, 163, 184, 0.7)' // slate-400, readable in both themes
const GRID_COLOR = 'rgba(148, 163, 184, 0.15)'

// Explicit hex fills matching tailwind.config.js `theme.extend.colors.risk`
// (canvas fills can't consume Tailwind classes, so the palette is
// duplicated here deliberately).
const RISK_HEX = {
  safe: '#22c55e',
  low: '#84cc16',
  medium: '#f59e0b',
  high: '#f97316',
  critical: '#ef4444',
}

const TOOLTIP_OPTIONS = {
  backgroundColor: '#1e293b',
  titleColor: '#f8fafc',
  bodyColor: '#e2e8f0',
  padding: 10,
  cornerRadius: 8,
  displayColors: false,
}

function ChartsSkeleton() {
  return (
    <div className="card space-y-4">
      <div className="h-4 w-32 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
      <div className="h-48 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
    </div>
  )
}

function ScoreTrendChart({ scoreTrend }) {
  const data = {
    labels: scoreTrend.map((point) =>
      new Date(point.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    ),
    datasets: [
      {
        label: 'Average safety score',
        data: scoreTrend.map((point) => point.averageScore),
        borderColor: '#2645e4',
        backgroundColor: 'rgba(38, 69, 228, 0.12)',
        fill: true,
        tension: 0.35,
        pointRadius: 2,
        pointHoverRadius: 4,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        ...TOOLTIP_OPTIONS,
        callbacks: {
          label: (context) => {
            const point = scoreTrend[context.dataIndex]
            return `Avg score: ${context.parsed.y} (${point.count} analyses)`
          },
        },
      },
    },
    scales: {
      y: {
        min: 0,
        max: 100,
        ticks: { color: AXIS_COLOR, stepSize: 25 },
        grid: { color: GRID_COLOR },
      },
      x: {
        ticks: { color: AXIS_COLOR, maxRotation: 0, autoSkip: true },
        grid: { display: false },
      },
    },
  }

  return (
    <div className="card">
      <h2 className="mb-4 text-base font-semibold text-slate-900 dark:text-white">
        Safety Score Trend
      </h2>
      <div className="h-56">
        <Line data={data} options={options} />
      </div>
    </div>
  )
}

function RiskDistributionChart({ riskLevelDistribution }) {
  const orderedRows = RISK_LEVEL_ORDER.map(
    (level) =>
      riskLevelDistribution.find((row) => row.riskLevel === level) ?? { riskLevel: level, count: 0 }
  )
  const total = orderedRows.reduce((sum, row) => sum + row.count, 0)

  const data = {
    labels: orderedRows.map((row) => getRiskLevelConfig(row.riskLevel).label),
    datasets: [
      {
        data: orderedRows.map((row) => row.count),
        backgroundColor: orderedRows.map((row) => RISK_HEX[row.riskLevel]),
        hoverOffset: 4,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: AXIS_COLOR, boxWidth: 10, padding: 12, font: { size: 11 } },
      },
      tooltip: {
        ...TOOLTIP_OPTIONS,
        callbacks: {
          label: (context) => {
            const pct = total > 0 ? Math.round((context.parsed / total) * 100) : 0
            return `${context.label}: ${context.parsed} (${pct}%)`
          },
        },
      },
    },
  }

  return (
    <div className="card">
      <h2 className="mb-4 text-base font-semibold text-slate-900 dark:text-white">
        Risk Level Distribution
      </h2>
      {total === 0 ? (
        <p className="py-14 text-center text-sm text-slate-400">No analyses yet.</p>
      ) : (
        <div className="h-56">
          <Doughnut data={data} options={options} />
        </div>
      )}
    </div>
  )
}

function DetectionBreakdownChart({ detectionBreakdown }) {
  const rows = [
    { label: 'Injection only', value: detectionBreakdown.injectionOnly, color: '#f97316' },
    { label: 'Toxicity only', value: detectionBreakdown.toxicityOnly, color: '#f59e0b' },
    { label: 'Both', value: detectionBreakdown.both, color: '#ef4444' },
    { label: 'Neither', value: detectionBreakdown.none, color: '#22c55e' },
  ]

  const data = {
    labels: rows.map((row) => row.label),
    datasets: [
      {
        label: 'Analyses',
        data: rows.map((row) => row.value),
        backgroundColor: rows.map((row) => row.color),
        borderRadius: 6,
        maxBarThickness: 40,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: { display: false },
      tooltip: TOOLTIP_OPTIONS,
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: { color: AXIS_COLOR, precision: 0 },
        grid: { color: GRID_COLOR },
      },
      y: {
        ticks: { color: AXIS_COLOR },
        grid: { display: false },
      },
    },
  }

  return (
    <div className="card">
      <h2 className="mb-4 text-base font-semibold text-slate-900 dark:text-white">
        Detection Breakdown
      </h2>
      <div className="h-56">
        <Bar data={data} options={options} />
      </div>
    </div>
  )
}

/**
 * Dashboard charts \u2014 Milestone 12, wired to the real backend
 * (GET /api/stats/charts via dashboardService.getDashboardCharts).
 *
 * Replaces the ChartsPlaceholder reserved-space component. Renders three
 * Chart.js visualizations: a score trend line, a risk-level distribution
 * donut, and a detection-type breakdown bar chart. All three read from
 * the single `charts` prop DashboardPage fetches once per load/refresh,
 * so there's no independent data fetching in this component.
 */
function DashboardCharts({ charts, isLoading }) {
  if (isLoading || !charts) {
    return (
      <div className="space-y-6">
        <ChartsSkeleton />
        <ChartsSkeleton />
      </div>
    )
  }

  const hasAnyData = charts.scoreTrend.some((point) => point.count > 0)

  return (
    <div className="space-y-6">
      <ScoreTrendChart scoreTrend={charts.scoreTrend} />
      <RiskDistributionChart riskLevelDistribution={charts.riskLevelDistribution} />
      <DetectionBreakdownChart detectionBreakdown={charts.detectionBreakdown} />
      {!hasAnyData && (
        <div className="card flex items-center gap-3 text-sm text-slate-400">
          <FiBarChart2 className="h-4 w-4 shrink-0" />
          Charts will fill in as you analyze more prompts.
        </div>
      )}
    </div>
  )
}

export default DashboardCharts
