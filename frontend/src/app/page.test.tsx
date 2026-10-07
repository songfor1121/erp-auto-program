import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import Home from './page'

describe('Home', () => {
  it('renders a heading', () => {
    render(<Home />)
    const container = screen.getByRole('main')
    expect(container).toBeInTheDocument()
  })
})
