import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { getGuideNextStep, GuideResponse } from '../api/client'

export default function GuidePage() {
  const { t } = useTranslation()
  const [guide, setGuide] = useState<GuideResponse | null>(null)
  const [history, setHistory] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchStep = useCallback(
    async (state: string) => {
      setLoading(true)
      setError('')
      try {
        const response = await getGuideNextStep(state)
        setGuide(response)
      } catch (err: unknown) {
        const errorMsg = err instanceof Error ? err.message : t('common.error')
        setError(errorMsg)
      } finally {
        setLoading(false)
      }
    },
    [t],
  )

  useEffect(() => {
    fetchStep('INIT')
  }, [fetchStep])

  const handleNext = () => {
    if (!guide) return
    setHistory([...history, guide.current_state])
    fetchStep(guide.next_state)
  }

  const handleBack = () => {
    if (history.length === 0) return
    const prevState = history[history.length - 1]
    setHistory(history.slice(0, -1))
    fetchStep(prevState)
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 animate-fade-in">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('guide.title')}</h1>
      <p className="text-gray-600 mb-8">{t('guide.description')}</p>

      {loading && (
        <div className="flex items-center justify-center py-12" role="status">
          <span className="spinner" aria-hidden="true" />
          <span className="ml-3 text-gray-500">{t('common.loading')}</span>
        </div>
      )}

      {error && (
        <div className="status-ineligible animate-slide-up" role="alert">
          <span aria-hidden="true">⚠️</span> {error}
        </div>
      )}

      {guide && !loading && (
        <div className="animate-slide-up" id="guide-content" role="status" aria-live="polite">
          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span aria-live="polite">
                {t('guide.step', { current: guide.step_number, total: guide.total_steps })}
              </span>
              <span className="badge-info" aria-live="polite">{guide.current_state.replace(/_/g, ' ')}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-gradient-to-r from-primary-600 to-primary-400 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${(guide.step_number / guide.total_steps) * 100}%` }}
                role="progressbar"
                aria-valuenow={guide.step_number}
                aria-valuemin={1}
                aria-valuemax={guide.total_steps}
                aria-label={t('guide.step', {
                  current: guide.step_number,
                  total: guide.total_steps,
                })}
              />
            </div>
          </div>

          {/* Instructions Card */}
          <div className="card mb-6" id="guide-instructions">
            <div className="whitespace-pre-line text-gray-800 leading-relaxed">
              {guide.instructions}
            </div>
          </div>

          {/* Links */}
          {guide.links.length > 0 && (
            <div className="card mb-6" id="guide-links">
              <h3 className="font-semibold text-gray-900 mb-3">
                <span aria-hidden="true">🔗</span> {t('guide.useful_links')}
              </h3>
              <div className="space-y-2">
                {guide.links.map((link, index) => (
                  <a
                    key={index}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 p-3 rounded-lg bg-primary-50 hover:bg-primary-100 transition-colors text-primary-700"
                  >
                    <span className="text-lg" aria-hidden="true">
                      {link.type === 'download' ? '⬇️' : link.type === 'portal' ? '🌐' : 'ℹ️'}
                    </span>
                    <span className="text-sm font-medium">{link.label || link.url}</span>
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex gap-4">
            {history.length > 0 && (
              <button onClick={handleBack} id="guide-back-btn" className="btn-secondary flex-1">
                <span aria-hidden="true">←</span> {t('guide.previous')}
              </button>
            )}
            {guide.next_state !== 'COMPLETE' && (
              <button onClick={handleNext} id="guide-next-btn" className="btn-primary flex-1">
                {t('guide.next')} <span aria-hidden="true">→</span>
              </button>
            )}
            {guide.current_state === 'COMPLETE' && (
              <div className="w-full text-center py-4">
                <p className="text-xl font-bold text-green-700">
                  <span aria-hidden="true">🎉</span> {t('guide.complete')}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
