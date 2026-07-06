import { useState } from 'react'
import { FiAlertTriangle } from 'react-icons/fi'
import PromptInputForm from '../components/Analyzer/PromptInputForm.jsx'
import AnalysisResult from '../components/Analyzer/AnalysisResult.jsx'
import { analyzePrompt } from '../services/analyzerService.js'

/**
 * Prompt Analyzer page. Submits a prompt to the real backend
 * (POST /api/analyze), which runs the injection/toxicity detectors and
 * scoring engine, persists the result for the authenticated user, and
 * returns the full analysis — displayed via AnalysisResult.
 */
function AnalyzerPage() {
  const [prompt, setPrompt] = useState('')
  const [result, setResult] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    setError(null)
    try {
      const response = await analyzePrompt(prompt)
      setResult(response)
    } catch (err) {
      setError(err.message || 'Failed to analyze this prompt. Please try again.')
      setResult(null)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleClear = () => {
    setPrompt('')
    setResult(null)
    setError(null)
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 py-10 sm:px-6 lg:px-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Prompt Analyzer</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Check a prompt for injection attempts and toxic language before it reaches your model.
        </p>
      </div>

      <PromptInputForm
        prompt={prompt}
        onPromptChange={setPrompt}
        onSubmit={handleAnalyze}
        onClear={handleClear}
        isAnalyzing={isAnalyzing}
      />

      {error && (
        <div className="flex items-start gap-2 rounded-lg border border-risk-critical/30 bg-risk-critical/10 px-4 py-3 text-sm text-risk-critical">
          <FiAlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {result && <AnalysisResult result={result} />}
    </div>
  )
}

export default AnalyzerPage
