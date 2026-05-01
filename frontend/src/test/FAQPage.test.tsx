import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import FAQPage from '../components/FAQPage'
import { askFAQ } from '../api/client'

vi.mock('../api/client', () => ({
  askFAQ: vi.fn(),
}))

const mockedAskFAQ = vi.mocked(askFAQ)

describe('FAQPage', () => {
  beforeEach(() => {
    mockedAskFAQ.mockReset()
  })

  it('submits a question and renders grounded citations', async () => {
    const user = userEvent.setup()
    mockedAskFAQ.mockResolvedValue({
      answer: 'You can register online using the official voter portal.',
      citations: [{ title: 'ECI Voter Registration', url: 'https://eci.gov.in/' }],
      locale: 'en-IN',
    })

    render(<FAQPage />)

    await user.type(screen.getByLabelText(/type your question/i), 'How do I register?')
    await user.click(screen.getByRole('button', { name: /ask question/i }))

    await waitFor(() => {
      expect(mockedAskFAQ).toHaveBeenCalledWith({
        query: 'How do I register?',
        locale: 'en-IN',
      })
    })
    expect(await screen.findByRole('status')).toHaveTextContent(/register online/i)
    expect(screen.getByRole('link', { name: /eci voter registration/i })).toHaveAttribute(
      'href',
      'https://eci.gov.in/',
    )
  })
})
