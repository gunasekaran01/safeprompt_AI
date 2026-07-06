import { FiAlertOctagon, FiCheckCircle, FiFileText, FiShieldOff } from 'react-icons/fi'
import SafetyScoreGauge from '../SafetyScoreGauge.jsx'
import RiskBadge from '../RiskBadge.jsx'
import DetectionStatusCard from './DetectionStatusCard.jsx'

function AnalysisResult({ result }) {
  return (
    <div className="card space-y-6">
      <div className="flex flex-col items-center gap-4 border-b border-slate-100 pb-6 dark:border-slate-700 sm:flex-row sm:justify-between">
        <div className="text-center sm:text-left">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Result</p>
          <div className="mt-1 flex items-center gap-2">
            <RiskBadge riskLevel={result.riskLevel} />
          </div>
        </div>
        <SafetyScoreGauge score={result.safetyScore} size={120} strokeWidth={10} />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <DetectionStatusCard
          icon={FiShieldOff}
          title="Prompt Injection"
          detected={result.injection.detected}
          confidence={result.injection.confidence}
          description={result.injection.reason}
        />
        <DetectionStatusCard
          icon={FiAlertOctagon}
          title="Toxicity"
          detected={result.toxicity.detected}
          confidence={result.toxicity.confidence}
          description={result.toxicity.explanation}
          extraLabel={result.toxicity.category !== 'none' ? `Category: ${result.toxicity.category}` : undefined}
        />
      </div>

      <div className="rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
        <div className="flex items-start gap-2">
          <FiCheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-brand-600 dark:text-brand-400" />
          <div>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">Recommendation</p>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{result.recommendation}</p>
          </div>
        </div>
      </div>

      <div className="flex items-start gap-2">
        <FiFileText className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
        <div>
          <p className="text-sm font-semibold text-slate-900 dark:text-white">Reasoning</p>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{result.reasoning}</p>
        </div>
      </div>
    </div>
  )
}

export default AnalysisResult
