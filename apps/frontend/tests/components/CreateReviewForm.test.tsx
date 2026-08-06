import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CreateReviewForm } from '../../src/components/CreateReviewForm';

jest.mock('../../src/api/endpoints/reviews', () => ({
  reviewsApi: {
    createReview: jest.fn(),
  },
}));

jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('CreateReviewForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders form fields', () => {
    render(<CreateReviewForm />);

    expect(screen.getByPlaceholderText(/github\.com\/user\/repo/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText('123')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create review/i })).toBeInTheDocument();
  });

  it('shows validation errors on empty submit', async () => {
    render(<CreateReviewForm />);

    const submitButton = screen.getByRole('button', { name: /create review/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/repository url is required/i)).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    const mockApi = require('../../src/api/endpoints/reviews');
    mockApi.reviewsApi.createReview.mockResolvedValue({
      id: 'test-id',
      status: 'pending',
    });

    render(<CreateReviewForm />);

    fireEvent.change(screen.getByPlaceholderText(/github\.com\/user\/repo/i), {
      target: { value: 'https://github.com/test/repo' },
    });
    fireEvent.change(screen.getByPlaceholderText('123'), {
      target: { value: '42' },
    });

    const submitButton = screen.getByRole('button', { name: /create review/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApi.reviewsApi.createReview).toHaveBeenCalledWith({
        repositoryUrl: 'https://github.com/test/repo',
        prNumber: 42,
      });
    });
  });
});
