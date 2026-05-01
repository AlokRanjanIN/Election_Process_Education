import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TimelinePage from '../components/TimelinePage'
import { getTimeline } from '../api/client'

vi.mock('../api/client', () => ({
  getTimeline: vi.fn(),
}))

const mockedGetTimeline = vi.mocked(getTimeline)

describe('TimelinePage', () => {
  beforeEach(() => {
    mockedGetTimeline.mockReset()
  })

  it('searches by state and renders election events', async () => {
    const user = userEvent.setup()
    mockedGetTimeline.mockResolvedValue([
      {
        constituency_id: 'MH-23',
        events: [{ phase: 'Polling Day', date: '2024-04-20T08:00:00Z' }],
      },
    ])

    render(<TimelinePage />)

    await user.selectOptions(screen.getByLabelText(/select state/i), 'MH')
    await user.click(screen.getByRole('button', { name: /search timeline/i }))

    await waitFor(() => {
      expect(mockedGetTimeline).toHaveBeenCalledWith('MH', undefined)
    })
    expect(await screen.findByRole('status')).toHaveTextContent(/polling day/i)
    expect(screen.getByText('MH-23')).toBeInTheDocument()
  })
})
