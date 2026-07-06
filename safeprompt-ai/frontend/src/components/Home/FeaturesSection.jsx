import {
  FiActivity,
  FiAlertOctagon,
  FiDownload,
  FiGrid,
  FiShieldOff,
  FiUnlock,
} from 'react-icons/fi'
import FeatureCard from './FeatureCard.jsx'

const FEATURES = [
  {
    icon: FiShieldOff,
    title: 'Prompt Injection Detection',
    description:
      'Flags attempts to override system instructions, such as "ignore previous instructions" or "reveal your system prompt".',
    accentClassName: 'bg-brand-600',
  },
  {
    icon: FiUnlock,
    title: 'Jailbreak Detection',
    description:
      'Catches role-play, "developer mode", and other framing designed to bypass an AI system\'s safety guardrails.',
    accentClassName: 'bg-risk-high',
  },
  {
    icon: FiAlertOctagon,
    title: 'Toxicity Detection',
    description:
      'Identifies profanity, harassment, threats, and hate speech using proven toxicity classification models.',
    accentClassName: 'bg-risk-critical',
  },
  {
    icon: FiActivity,
    title: 'Safety Scoring',
    description:
      'Every prompt gets a 0–100 safety score and a five-tier risk level, from Safe to Critical, with clear reasoning.',
    accentClassName: 'bg-risk-medium',
  },
  {
    icon: FiGrid,
    title: 'Analytics Dashboard',
    description:
      'Track total analyses, safe vs. unsafe ratios, and injection/toxicity trends at a glance with live charts.',
    accentClassName: 'bg-brand-500',
  },
  {
    icon: FiDownload,
    title: 'Exportable Reports',
    description:
      'Download a polished PDF report for any analysis — prompt, results, score, and recommendation included.',
    accentClassName: 'bg-risk-safe',
  },
]

function FeaturesSection() {
  return (
    <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          Everything you need to vet a prompt
        </h2>
        <p className="mt-3 text-slate-500 dark:text-slate-400">
          One platform for injection detection, toxicity screening, and
          explainable safety scoring.
        </p>
      </div>

      <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((feature) => (
          <FeatureCard key={feature.title} {...feature} />
        ))}
      </div>
    </section>
  )
}

export default FeaturesSection
