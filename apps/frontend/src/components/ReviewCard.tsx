// ============================================================
// CodeWhisper PR - ReviewCard Component
// ============================================================

import React from 'react';
import Link from 'next/link';
import { Review } from '../types';
import { formatDate, formatTokens, formatPercentage, getStatusColor, getStatusIcon, getRepositoryName } from '../utils';

interface ReviewCardProps {
  review: Review;
}

export function ReviewCard({ review }: ReviewCardProps) {
  return (
    <Link href={`/reviews/${review.id}`}>
      <a className="card hover:border-primary-500 transition-colors cursor-pointer block">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">
              {review.prTitle || `PR #${review.prNumber}`}
            </h3>
            <p className="text-sm text-gray-400">
              {getRepositoryName(review.repositoryUrl)}
            </p>
          </div>
          <span className={`badge ${getStatusColor(review.status)}`}>
            {getStatusIcon(review.status)} {review.status}
          </span>
        </div>

        {review.summary && (
          <p className="text-sm text-gray-300 mb-4 line-clamp-2">
            {review.summary}
          </p>
        )}

        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-white">
              {formatTokens(review.originalTokens || 0)}
            </p>
            <p className="text-xs text-gray-400">Original Tokens</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-green-400">
              {formatTokens(review.optimizedTokens || 0)}
            </p>
            <p className="text-xs text-gray-400">Optimized Tokens</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-primary-400">
              {formatPercentage(review.tokensSavedPercentage)}
            </p>
            <p className="text-xs text-gray-400">Tokens Saved</p>
          </div>
        </div>

        <div className="mt-4 text-xs text-gray-500">
          Created: {formatDate(review.createdAt)}
        </div>
      </a>
    </Link>
  );
}
