import { useTranslation } from 'react-i18next'

interface SpeechRecognitionResultEvent extends Event {
  results: SpeechRecognitionResultList
}

interface BrowserSpeechRecognition extends EventTarget {
  lang: string
  interimResults: boolean
  onresult: ((event: SpeechRecognitionResultEvent) => void) | null
  start: () => void
}

interface SpeechRecognitionConstructor {
  new (): BrowserSpeechRecognition
}

interface WindowWithSpeechRecognition extends Window {
  SpeechRecognition?: SpeechRecognitionConstructor
  webkitSpeechRecognition?: SpeechRecognitionConstructor
}

/**
 * Custom hook to handle Web Speech API interactions (Voice Input & TTS).
 */
export function useSpeech() {
  const { i18n } = useTranslation()
  const locale = i18n.language === 'hi' ? 'hi-IN' : 'en-IN'

  /**
   * Start voice recognition and call onResult with the transcript.
   */
  const startVoiceInput = (onResult: (transcript: string) => void) => {
    const speechWindow = window as WindowWithSpeechRecognition
    const SpeechRecognition = speechWindow.webkitSpeechRecognition || speechWindow.SpeechRecognition

    if (!SpeechRecognition) {
      console.warn('Speech recognition not supported')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = locale
    recognition.interimResults = false
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      onResult(transcript)
    }
    recognition.start()
  }

  /**
   * Read aloud the provided text.
   */
  const readAloud = (text: string) => {
    if (!text) return
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = locale
    utterance.rate = 0.9
    window.speechSynthesis.speak(utterance)
  }

  return { startVoiceInput, readAloud }
}
