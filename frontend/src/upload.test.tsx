import '@testing-library/jest-dom'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import UploadArea from './components/UploadArea'
import * as api from './lib/api'

// Mock next router
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush })
}));

// Mock API
jest.mock('./lib/api', () => ({
  uploadDocument: jest.fn()
}));

describe('UploadArea', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders upload text', () => {
    render(<UploadArea />)
    expect(screen.getByText(/거래명세서 촬영 또는 업로드/i)).toBeInTheDocument()
  })

  it('handles file upload and redirects', async () => {
    (api.uploadDocument as jest.Mock).mockResolvedValueOnce({ document_id: 123 });

    render(<UploadArea />);
    const input = screen.getByTestId('file-upload');

    // Simulate file selection
    const file = new File(['dummy'], 'test.png', { type: 'image/png' });
    fireEvent.change(input, { target: { files: [file] } });

    // Check loading state
    expect(screen.getByText(/거래명세서를 분석하고 있습니다/i)).toBeInTheDocument();

    // Check redirect
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/review/123');
    });
  })

  it('handles upload failure', async () => {
    const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});
    (api.uploadDocument as jest.Mock).mockRejectedValueOnce(new Error('Failed'));

    render(<UploadArea />);
    const input = screen.getByTestId('file-upload');

    const file = new File(['dummy'], 'test.txt', { type: 'text/plain' });
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith('업로드에 실패했습니다. (이미지나 PDF를 선택해주세요)');
    });
    alertMock.mockRestore();
  })
})
