import { FiCpu, FiEdit3, FiFileText } from 'react-icons/fi'

const STEPS = [
  {
    icon: FiEdit3,
    title: 'Submit a Prompt',
    description: 'Paste or type any prompt into the analyzer — no setup required.',
  },
  {
    icon: FiCpu,
    title: 'AI Analyzes It',
    description:
      'The injection detector and toxicity detector run in parallel to evaluate the prompt.',
  },
  {
    icon: FiFileText,
    title: 'Get Your Report',
    description:
      'Receive a safety score, risk level, and plain-language recommendation with reasoning.',
  },
]

function HowItWorksSection() {
  return (
    <section className="bg-slate-50 py-20 dark:bg-slate-900/40">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            How it works
          </h2>
          <p className="mt-3 text-slate-500 dark:text-slate-400">
            Three steps from raw prompt to explainable safety verdict.
          </p>
        </div>

        <div className="relative mt-12 grid grid-cols-1 gap-8 sm:grid-cols-3">
          {STEPS.map((step, index) => (
            <div key={step.title} className="relative text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-600 text-white shadow-card">
                <step.icon className="h-6 w-6" />
              </div>
              <div className="mx-auto mt-3 flex h-6 w-6 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white dark:bg-white dark:text-slate-900">
                {index + 1}
              </div>
              <h3 className="mt-3 text-base font-semibold text-slate-900 dark:text-white">
                {step.title}
              </h3>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default HowItWorksSection
