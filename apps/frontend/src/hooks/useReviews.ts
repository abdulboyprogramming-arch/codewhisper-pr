// ============================================================
// CodeWhisper PR - useReviews Hook
// ============================================================

import { useQuery, useMutation, useQueryClient } from 'react-query';
import { reviewsApi, CreateReviewRequest } from '../api/endpoints/reviews';
import { toast } from 'react-toastify';

export function useReviews() {
  const queryClient = useQueryClient();

  const listReviews = (params?: { page?: number; limit?: number; status?: string }) => {
    return useQuery(['reviews', params], () => reviewsApi.listReviews(params));
  };

  const getReview = (id: string) => {
    return useQuery(['review', id], () => reviewsApi.getReview(id), {
      enabled: !!id,
    });
  };

  const getReviewStatus = (id: string) => {
    return useQuery(['review-status', id], () => reviewsApi.getReviewStatus(id), {
      enabled: !!id,
      refetchInterval: (data: any) => {
        if (data?.status === 'pending' || data?.status === 'processing') {
          return 2000;
        }
        return false;
      },
    });
  };

  const createReview = useMutation(reviewsApi.createReview, {
    onSuccess: () => {
      queryClient.invalidateQueries(['reviews']);
      queryClient.invalidateQueries(['dashboardStats']);
      toast.success('Review created successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create review');
    },
  });

  return { listReviews, getReview, getReviewStatus, createReview };
}
