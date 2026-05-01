import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { askFAQ, FAQResponse } from '../api/client'

/**
 * Custom hook to manage FAQ RAG pipeline state and API calls.
 */
export function useFAQ() {
  const { t, i18n } = useTranslation()
  const [result, setResult] = useState<FAQResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const locale = i18n.language === 'hi' ? 'hi-IN' : 'en-IN'

  const handleAsk = async (query: string) => {
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

  const resetFAQ = () => {
    setResult(null)
    setError('')
  }

  return { result, loading, error, handleAsk, resetFAQ }
}
