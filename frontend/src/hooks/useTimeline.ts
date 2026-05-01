import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getTimeline, TimelineResponse } from '../api/client'

/**
 * Custom hook to manage election timeline state and API calls.
 */
export function useTimeline() {
  const { t } = useTranslation()
  const [timelines, setTimelines] = useState<TimelineResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const fetchTimeline = async (stateCode: string, constituencyId?: string) => {
    setLoading(true)
    setError('')
    setSearched(true)

    try {
      const results = await getTimeline(stateCode, constituencyId || undefined)
      setTimelines(results)
    } catch (err: unknown) {
      setTimelines([])
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { status?: number } }
        if (axiosErr.response?.status === 404) {
          setError(t('timeline.no_results'))
        } else {
          setError(t('common.error'))
        }
      } else {
        setError(t('common.error'))
      }
    } finally {
      setLoading(false)
    }
  }

  return { timelines, loading, error, searched, fetchTimeline }
}
