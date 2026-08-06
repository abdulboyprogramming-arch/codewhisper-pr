// ============================================================
// CodeWhisper PR - Reviews List Page
// ============================================================

import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { useRouter } from 'next/router';
import { reviewsApi, ReviewsListResponse } from '../src/api/endpoints/reviews';
import { Layout } from '../src/components/Layout';
import { ProtectedRoute } from '../src/components/ProtectedRoute';
import { ReviewCard } from '../src/components/ReviewCard';
import LoadingSpinner from '../src/components/LoadingSpinner';
import Head from 'next/head';

export default function Reviews() {
  return (
    <ProtectedRoute>
      <Layout>
        <Head>
          <title>Reviews - CodeWhisper PR</title>
        </Head>
        <ReviewsContent />
      </Layout>
    </ProtectedRoute>
  );
}

function ReviewsContent() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();

  const { data, isLoading, error } = useQuery(['reviews', page, statusFilter], async () => {
    const response = await reviewsApi.listReviews({
      page,
      limit: 10,
      status: statusFilter,
    });
    return response;
  });

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value || undefined;
    setStatusFilter(value);
    setPage(1);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return <div className="text-center text-secondary-400">Error loading reviews</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Reviews</h1>
        <div className="flex gap-2">
          <select
            value={statusFilter || ''}
            onChange={handleStatusChange}
            className="input w-auto"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      <div className="space-y-3">
        {data?.items?.map((review) => (
          <ReviewCard key={review.id} review={review} />
        ))}
      </div>

      {data && data.total_pages > 1 && (
        <div className="flex justify-center gap-2 mt-6">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="btn btn-secondary"
          >
            Previous
          </button>
          <span className="text-gray-400 px-3 py-1">
            Page {page} of {data.total_pages}
          </span>
          <button
            onClick={() => setPage(Math.min(data.total_pages, page + 1))}
            disabled={page === data.total_pages}
            className="btn btn-secondary"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
