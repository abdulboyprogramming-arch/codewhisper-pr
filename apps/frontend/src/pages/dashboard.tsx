// ============================================================
// CodeWhisper PR - Dashboard Page
// ============================================================

import React from 'react';
import { useQuery } from 'react-query';
import { reviewsApi } from '../src/api/endpoints/reviews';
import { extractData } from '../src/api/interceptors';
import { Layout } from '../src/components/Layout';
import { ProtectedRoute } from '../src/components/ProtectedRoute';
import { ReviewCard } from '../src/components/ReviewCard';
import { CreateReviewForm } from '../src/components/CreateReviewForm';
import { formatTokens, formatPercentage } from '../src/utils';
import LoadingSpinner from '../src/components/LoadingSpinner';
import Head from 'next/head';

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <Layout>
        <Head>
          <title>Dashboard - CodeWhisper PR</title>
        </Head>
        <DashboardContent />
      </Layout>
    </ProtectedRoute>
  );
}

function DashboardContent() {
  const { data: stats, isLoading: statsLoading } = useQuery('dashboardStats', async () => {
    const response = await reviewsApi.getDashboardStats();
    return response;
  });

  const { data: reviewsData, isLoading: reviewsLoading } = useQuery('recentReviews', async () => {
    const response = await reviewsApi.listReviews({ limit: 3 });
    return response;
  });

  if (statsLoading || reviewsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm text-gray-400 mb-1">Total Reviews</p>
          <p className="text-2xl font-bold text-white">{stats?.totalReviews || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-400 mb-1">Tokens Saved</p>
          <p className="text-2xl font-bold text-green-400">{formatTokens(stats?.totalTokensSaved || 0)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-400 mb-1">Avg Savings</p>
          <p className="text-2xl font-bold text-primary-400">{formatPercentage(stats?.averageSavingsPercentage)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-400 mb-1">Cost Saved</p>
          <p className="text-2xl font-bold text-blue-400">${stats?.totalCostSaved?.toFixed(2) || '0.00'}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Create New Review</h2>
          <CreateReviewForm />
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Recent Reviews</h2>
          {reviewsData?.items && reviewsData.items.length > 0 ? (
            <div className="space-y-3">
              {reviewsData.items.map((review) => (
                <ReviewCard key={review.id} review={review} />
              ))}
            </div>
          ) : (
            <p className="text-gray-400">No recent reviews</p>
          )}
        </div>
      </div>
    </div>
  );
}

export async function getServerSideProps() {
  return { props: {} };
}
