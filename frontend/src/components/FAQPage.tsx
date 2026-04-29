import { useState, FormEvent, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { askFAQ, FAQResponse } from '../api/client'

export default function FAQPage() {
  const { t, i18n } = useTranslation()
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<FAQResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const locale = i18n.language === 'hi' ? 'hi-IN' : 'en-IN'

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await askFAQ({ query: query.trim(), locale })
      setResult(response)
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : t('common.error')
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  // --- Web Speech API: Voice Input ---
  const handleVoiceInput = () => {
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
    if (!SpeechRecognition) {
      alert('Voice input is not supported in this browser.')
      return
    }
    const recognition = new SpeechRecognition()
    recognition.lang = locale
    recognition.interimResults = false
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      setQuery(transcript)
    }
    recognition.start()
  }

  // --- Web Speech API: Text-to-Speech ---
  const handleReadAloud = () => {
    if (!result?.answer) return
    const utterance = new SpeechSynthesisUtterance(result.answer)
    utterance.lang = locale
    utterance.rate = 0.9
    speechSynthesis.speak(utterance)
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 animate-fade-in">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('faq.title')}</h1>
      <p className="text-gray-600 mb-8">{t('faq.description')}</p>

      <form onSubmit={handleSubmit} className="card space-y-4 mb-8" id="faq-form">
        <div className="relative">
          <textarea
            ref={inputRef}
            id="faq-query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t('faq.placeholder')}
            maxLength={300}
            rows={3}
            className="input-field resize-none pr-12"
            required
          />
          <span className="absolute bottom-3 right-3 text-xs text-gray-400">
            {query.length}/300
          </span>
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            id="ask-faq-btn"
            disabled={loading || !query.trim()}
            className="btn-primary flex-1 flex items-center justify-center gap-2"
          >
            {loading && <span className="spinner" />}
            {t('faq.ask')}
          </button>

          <button
            type="button"
            onClick={handleVoiceInput}
            id="voice-input-btn"
            className="btn-secondary px-4"
            title={t('faq.voice_input')}
          >
            🎤
          </button>
        </div>

        <p className="text-xs text-gray-400 text-center">{t('faq.powered_by')}</p>
      </form>

      {error && (
        <div className="status-ineligible animate-slide-up" id="faq-error">
          ⚠️ {error}
        </div>
      )}

      {result && (
        <div className="animate-slide-up space-y-4" id="faq-result">
          {/* Answer */}
          <div className="card">
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-semibold text-gray-900">💡 Answer</h3>
              <button
                onClick={handleReadAloud}
                id="read-aloud-btn"
                className="text-primary-600 hover:text-primary-800 p-2 rounded-lg hover:bg-primary-50 transition-colors min-h-0 min-w-0"
                title={t('faq.voice_output')}
              >
                🔊
              </button>
            </div>
            <p className="text-gray-800 leading-relaxed whitespace-pre-line">
              {result.answer}
            </p>
          </div>

          {/* Citations */}
          {result.citations.length > 0 && (
            <div className="card" id="faq-citations">
              <h3 className="font-semibold text-gray-900 mb-3">📚 {t('faq.sources')}</h3>
              <div className="space-y-2">
                {result.citations.map((citation, index) => (
                  <a
                    key={index}
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 p-3 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors text-blue-700 text-sm"
                  >
                    <span>📄</span>
                    <span className="font-medium">{citation.title}</span>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
