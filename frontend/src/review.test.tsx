import '@testing-library/jest-dom'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ReviewField from './components/ReviewField'
import * as api from './lib/api'

jest.mock('./lib/api', () => ({
  updateField: jest.fn()
}));

describe('ReviewField', () => {
  const mockFieldData = {
    raw_value: "ABC Corp",
    normalized_value: "ABC Corp",
    confidence: 0.99,
    validation_status: "PENDING",
    source: "AI",
    validation_message: ""
  };

  const mockNeedsReviewData = {
    ...mockFieldData,
    confidence: 0.85,
    validation_status: "NEEDS_REVIEW",
    validation_message: "Low confidence"
  };

  it('renders normal field correctly with checkmark', () => {
    render(<ReviewField docId={1} label="회사명" fieldName="company_name" data={mockFieldData} onDataUpdated={jest.fn()} />);
    expect(screen.getByText('회사명')).toBeInTheDocument();
    expect(screen.getByDisplayValue('ABC Corp')).toBeInTheDocument();
    expect(screen.getByText('✓')).toBeInTheDocument();
  });

  it('renders low confidence field with warning', () => {
    render(<ReviewField docId={1} label="회사명" fieldName="company_name" data={mockNeedsReviewData} onDataUpdated={jest.fn()} />);
    expect(screen.getByText(/확인 필요/)).toBeInTheDocument();
    expect(screen.getByText('Low confidence')).toBeInTheDocument();
  });

  it('calls update API on blur when value changed', async () => {
    (api.updateField as jest.Mock).mockResolvedValueOnce({ message: "Updated" });

    render(<ReviewField docId={1} label="회사명" fieldName="company_name" data={mockFieldData} onDataUpdated={jest.fn()} />);
    const input = screen.getByTestId('input-company_name');

    fireEvent.change(input, { target: { value: 'New Corp' } });
    fireEvent.blur(input);

    await waitFor(() => {
      expect(api.updateField).toHaveBeenCalledWith(1, 'company_name', 'New Corp', undefined);
    });
  });

})
