// ============================================================
// CodeWhisper PR - CreateReviewForm Component
// ============================================================

import React from 'react';
import { useForm } from 'react-hook-form';
import { useReviews } from '../hooks/useReviews';
import LoadingSpinner from './LoadingSpinner';

interface CreateReviewFormData {
  repositoryUrl: string;
  prNumber: number;
}

export function CreateReviewForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<CreateReviewFormData>();
  const { createReview } = useReviews();

  const onSubmit = async (data: CreateReviewFormData) => {
    await createReview.mutateAsync({
      repositoryUrl: data.repositoryUrl,
      prNumber: data.prNumber,
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Repository URL
        </label>
        <input
          type="url"
          placeholder="https://github.com/user/repo"
          className="input"
          {...register('repositoryUrl', { required: 'Repository URL is required' })}
        />
        {errors.repositoryUrl && (
          <p className="text-sm text-secondary-400 mt-1">{errors.repositoryUrl.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          PR Number
        </label>
        <input
          type="number"
          placeholder="123"
          className="input"
          {...register('prNumber', {
            required: 'PR number is required',
            valueAsNumber: true,
            min: 1,
          })}
        />
        {errors.prNumber && (
          <p className="text-sm text-secondary-400 mt-1">{errors.prNumber.message}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={createReview.isLoading}
        className="btn btn-primary w-full"
      >
        {createReview.isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <LoadingSpinner size="sm" />
            Creating Review...
          </span>
        ) : (
          'Create Review'
        )}
      </button>
    </form>
  );
}
