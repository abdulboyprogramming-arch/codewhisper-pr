// ============================================================
// CodeWhisper PR - Index Page (Redirect to Dashboard)
// ============================================================

import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../src/hooks/useAuth';
import Head from 'next/head';

export default function Index() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      router.replace(isAuthenticated ? '/dashboard' : '/login');
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <>
      <Head>
        <title>CodeWhisper PR</title>
      </Head>
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="animate-pulse text-gray-400">Loading...</div>
      </div>
    </>
  );
}
