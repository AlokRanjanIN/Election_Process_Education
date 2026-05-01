import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { evaluateEligibility, EligibilityResponse, EligibilityRequest } from '../api/client'

/**
 * Custom hook to manage voter eligibility state and API calls.
 */
export function useEligibility() {
  const { t } = useTranslation()
  const [result, setResult] = useState<EligibilityResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const checkEligibility = async (data: EligibilityRequest) => {
    setError('')
    setResult(null)
    setLoading(true)

    try {
      const response = await evaluateEligibility(data)
      setResult(response)
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : t('common.error')
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return { result, loading, error, checkEligibility }
}
