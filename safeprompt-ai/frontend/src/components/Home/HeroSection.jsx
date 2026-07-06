import { Link } from 'react-router-dom'
import { FiArrowRight, FiCheckCircle, FiShield } from 'react-icons/fi'

const TRUST_BADGES = ['Explainable Reasoning', 'Self-Hosted', 'Open Detection Engine']

function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      {/* Soft gradient backdrop */}
      <div
        className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-b from-brand-50 via-white to-white dark:from-brand-900/20 dark:via-surface-dark dark:to-surface-dark"
        aria-hidden="true"
      />

      <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:py-24 lg:px-8">
        {/* Left: copy + CTAs */}
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-4 py-1.5 text-xs font-semibold text-brand-700 dark:border-brand-800 dark:bg-brand-900/30 dark:text-brand-300">
            <FiShield className="h-3.5 w-3.5" />
            AI Safety Platform
          </div>

          <h1 className="text-4xl font-extrabold leading-tight tracking-tight text-slate-900 dark:text-white sm:text-5xl">
            Catch prompt injection and toxicity before it reaches your model.
          </h1>

          <p className="max-w-xl text-lg text-slate-600 dark:text-slate-300">
            SafePrompt AI analyzes any prompt for jailbreak attempts, instruction
            overrides, and toxic language — then returns a clear safety score,
            risk level, and explainable recommendation in seconds.
          </p>

          <div className="flex flex-wrap gap-3">
            <Link to="/analyzer" className="btn-primary">
              Analyze a Prompt <FiArrowRight />
            </Link>
            <Link to="/dashboard" className="btn-secondary">
              View Dashboard
            </Link>
          </div>

          <div className="flex flex-wrap gap-x-6 gap-y-2 pt-2">
            {TRUST_BADGES.map((badge) => (
              <div
                key={badge}
                className="flex items-center gap-1.5 text-xs font-medium text-slate-500 dark:text-slate-400"
              >
                <FiCheckCircle className="h-3.5 w-3.5 text-risk-safe" />
                {badge}
              </div>
            ))}
          </div>
        </div>

        {/* Right: static demo result card */}
        <div className="relative">
          <div className="card mx-auto max-w-sm space-y-4 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Sample Analysis
              </span>
              <span className="rounded-full bg-risk-safe/10 px-2.5 py-1 text-xs font-semibold text-risk-safe">
                Safe
              </span>
            </div>

            <p className="rounded-lg bg-slate-50 p-3 text-sm text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              &ldquo;Summarize the key points from this quarterly report.&rdquo;
            </p>

            <div>
              <div className="mb-1 flex items-center justify-between text-xs">
                <span className="font-medium text-slate-500 dark:text-slate-400">Safety Score</span>
                <span className="font-bold text-risk-safe">96 / 100</span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                <div className="h-full rounded-full bg-risk-safe" style={{ width: '96%' }} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="rounded-lg border border-slate-100 p-2.5 dark:border-slate-700">
                <p className="text-slate-400">Injection</p>
                <p className="font-semibold text-risk-safe">Not Detected</p>
              </div>
              <div className="rounded-lg border border-slate-100 p-2.5 dark:border-slate-700">
                <p className="text-slate-400">Toxicity</p>
                <p className="font-semibold text-risk-safe">Not Detected</p>
              </div>
            </div>

            <p className="text-xs text-slate-500 dark:text-slate-400">
              Recommendation: Safe to process. No suspicious instructions or
              harmful language detected.
            </p>
          </div>

          {/* Decorative floating badge */}
          <div className="card absolute -bottom-4 -left-4 hidden w-40 items-center gap-2 py-3 sm:flex">
            <FiShield className="h-5 w-5 text-brand-600" />
            <div>
              <p className="text-xs font-semibold text-slate-900 dark:text-white">5 Risk Levels</p>
              <p className="text-[10px] text-slate-400">Safe → Critical</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default HeroSection
