// ============================================================
// CodeWhisper PR - Analytics Page
// ============================================================

import React from 'react';
import { useQuery } from 'react-query';
import { analyticsApi } from '../src/api/endpoints/reviews';
import { Layout } from '../src/components/Layout';
import { ProtectedRoute } from '../src/components/ProtectedRoute';
import { formatTokens, formatPercentage } from '../src/utils';
import LoadingSpinner from '../src/components/LoadingSpinner';
import Head from 'next/head';

export default function Analytics() {
  return (
    <ProtectedRoute>
      <Layout>
        <Head>
          <title>Analytics - CodeWhisper PR</title>
        </Head>
        <AnalyticsContent />
      </Layout>
    </ProtectedRoute>
  );
}

function AnalyticsContent() {
  const { data: overview, isLoading: overviewLoading } = useQuery('analyticsOverview', () =>
    analyticsApi.getOverview('weekly')
  );

  const { data: trendData, isLoading: trendLoading } = useQuery('tokenSavingsTrend', () =>
    analyticsApi.getTokenSavingsTrend(30)
  );

  if (overviewLoading || trendLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Analytics</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <p className="text-sm text-gray-400 mb-1">Total Reviews</p>
          <p className="text-2xl font-bold text-white">{overview?.totalReviews || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-400 mb-1">Total Tokens Saved</p>
          <p className="text-2xl font-bold text-green-400">{formatTokens(overview?.totalTokensSaved || 0)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-400 mb-1">Average Savings</p>
          <p className="text-2xl font-bold text-primary-400">{formatPercentage(overview?.averageSavingsPercentage || 0)}</p>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-3">Token Savings Trend</h2>
        <div className="h-64 flex items-end gap-2">
          {trendData?.values?.map((value, index) => (
            <div key={index} className="flex-1">
              <div
                className="bg-primary-600 rounded-t-lg transition-all hover:bg-primary-500"
                style={{ height: `${(value / Math.max(...trendData.values)) * 100}%` }}
              />
              <p className="text-xs text-gray-500 mt-1">{trendData.labels?.[index]}</p>
            </div>
          )) || []}
        </div>
      </div>
    </div>
  );
}
