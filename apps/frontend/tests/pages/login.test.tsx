import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientClient, QueryClientProvider } from 'react-query';
import { LoginPage } from '../../src/components/auth/LoginForm';

jest.mock('next/router', () => ({
  useRouter: () => ({
    replace: jest.fn(),
  }),
}));

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

describe('LoginPage', () => {
  it('renders login form', async () => {
    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <LoginPage />
      </QueryClientProvider>
    );

    expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/you@example.com/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText('••••••••').length).toBeGreaterThan(0);
  });

  it('shows validation errors on empty submit', async () => {
    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <LoginPage />
      </QueryClientProvider>
    );

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    submitButton.click();

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    });
  });
});
