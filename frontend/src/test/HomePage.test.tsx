import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import HomePage from '../components/HomePage'

describe('HomePage', () => {
  it('renders core voter education actions', () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>,
    )

    expect(screen.getByRole('heading', { name: /election guide india/i })).toBeInTheDocument()
    expect(screen.getAllByRole('link', { name: /check eligibility/i })[0]).toHaveAttribute(
      'href',
      '/eligibility',
    )
    expect(screen.getByRole('link', { name: /registration guide/i })).toHaveAttribute(
      'href',
      '/guide',
    )
    expect(screen.getByRole('link', { name: /election timeline/i })).toHaveAttribute(
      'href',
      '/timeline',
    )
  })
})
