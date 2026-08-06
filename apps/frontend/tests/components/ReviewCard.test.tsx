import { render, screen } from '@testing-library/react';
import { ReviewCard } from '../../src/components/ReviewCard';

const mockReview = {
  id: 'test-review-id',
  userId: 'user-1',
  repositoryUrl: 'https://github.com/test/repo',
  repositoryName: 'test/repo',
  prNumber: 42,
  prTitle: 'Fix bug in processing',
  prDescription: 'This PR fixes a bug',
  status: 'completed',
  diffContent: null,
  affectedFiles: null,
  originalTokens: 15000,
  optimizedTokens: 3900,
  tokensSavedPercentage: 74.0,
  optimizationTimeMs: 245,
  reviewOutput: null,
  summary: 'The code changes improve string processing.',
  issuesFound: null,
  modelUsed: 'gpt-4',
  createdAt: '2024-01-15T10:30:00Z',
  updatedAt: '2024-01-15T10:35:00Z',
  completedAt: '2024-01-15T10:35:00Z',
};

describe('ReviewCard', () => {
  it('renders review information', () => {
    render(<ReviewCard review={mockReview as any} />);

    expect(screen.getByText('Fix bug in processing')).toBeInTheDocument();
    expect(screen.getByText('completed')).toBeInTheDocument();
    expect(screen.getByText('74.0%')).toBeInTheDocument();
  });

  it('renders default title for PR without title', () => {
    render(<ReviewCard review={{ ...mockReview, prTitle: null } as any} />);

    expect(screen.getByText('PR #42')).toBeInTheDocument();
  });

  it('renders summary if present', () => {
    render(<ReviewCard review={mockReview as any} />);

    expect(screen.getByText(/code changes improve string processing/i)).toBeInTheDocument();
  });

  it('renders formatted values when tokens are present', () => {
    render(<ReviewCard review={mockReview as any} />);

    expect(screen.getByText('15.0K')).toBeInTheDocument();
    expect(screen.getByText('3.9K')).toBeInTheDocument();
  });

  it('handles null token values gracefully', () => {
    render(<ReviewCard review={{
      ...mockReview,
      originalTokens: null,
      optimizedTokens: null,
      tokensSavedPercentage: null,
    } as any} />);

    expect(screen.getAllByText('—').length).toBeGreaterThan(0);
  });
});
