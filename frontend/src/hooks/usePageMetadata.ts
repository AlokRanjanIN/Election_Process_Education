import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useLocation } from 'react-router-dom'

/**
 * Custom hook to dynamically update document title and SEO meta based on the current route.
 */
export function usePageMetadata() {
  const { t, i18n } = useTranslation()
  const location = useLocation()

  useEffect(() => {
    // Determine translation key based on path
    let key = 'home'
    const path = location.pathname.substring(1)
    if (path) key = path

    const baseTitle = t('app.title')
    const pageTitle = t(`nav.${key}`)
    
    // Update Document Title
    document.title = `${pageTitle} | ${baseTitle}`

    // Update Meta Description if it exists
    const metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute('content', t('app.tagline'))
    }
  }, [location.pathname, t, i18n.language])
}
