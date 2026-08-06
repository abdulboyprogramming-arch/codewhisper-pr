// ============================================================
// CodeWhisper PR - Review Detail Page
// ============================================================

import React from 'react';
import { useQuery } from 'react-query';
import { useRouter } from 'next/router';
import { reviewsApi, Review } from '../src/api/endpoints/reviews';
import { Layout } from '../src/components/Layout';
import { ProtectedRoute } from '../src/components/ProtectedRoute';
import LoadingSpinner from '../src/components/LoadingSpinner';
import { formatDate, formatTokens, formatPercentage, formatDuration, getStatusColor } from '../src/utils';
import Head from 'next/head';

export default function ReviewDetail() {
  return (
    <ProtectedRoute>
      <Layout>
        <Head>
          <title>Review - CodeWhisper PR</title>
        </Head>
        <ReviewDetailContent />
      </Layout>
    </ProtectedRoute>
  );
}

function ReviewDetailContent() {
  const router = useRouter();
  const { id } = router.query;
  const { data: review, isLoading, error } = useQuery(['review', id], () => reviewsApi.getReview(id!), {
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !review) {
    return <div className="text-center text-secondary-400">Review not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">{review.prTitle || `PR #${review.prNumber}`}</h1>
        <span className={`badge ${getStatusColor(review.status)}`}>
          {review.status}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm text-gray-400 mb-1">Original Tokens</p>
          <p className="text-xl font-bold text-white">{formatTokens(review.originalTokens || 0)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-400 mb-1">Optimized Tokens</p>
          <p className="text-xl font-bold text-green-400">{formatTokens(review.optimizedTokens || 0)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-400 mb-1">Tokens Saved</p>
          <p className="text-xl font-bold text-primary-400">{formatPercentage(review.tokensSavedPercentage)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-400 mb-1">Processing Time</p>
          <p className="text-xl font-bold text-blue-400">{formatDuration(review.optimizationTimeMs || 0)}</p>
        </div>
      </div>

      {review.summary && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-3">Summary</h2>
          <p className="text-gray-300 whitespace-pre-wrap">{review.summary}</p>
        </div>
      )}

      {review.diffContent && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-3">Diff</h2>
          <pre className="bg-gray-900 p-4 rounded-lg overflow-x-auto text-sm text-gray-300">
            <code>{review.diffContent}</code>
          </pre>
        </div>
      )}

      {review.reviewOutput && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-3">Review Output</h2>
          <pre className="bg-gray-900 p-4 rounded-lg overflow-x-auto text-sm text-gray-300">
            <code>{JSON.stringify(review.reviewOutput, null, 2)}</code>
          </pre>
        </div>
      )}

      <div className="text-sm text-gray-500">
        Created: {formatDate(review.createdAt)} | Updated: {formatDate(review.updatedAt)}
      </div>
    </div>
  );
}
