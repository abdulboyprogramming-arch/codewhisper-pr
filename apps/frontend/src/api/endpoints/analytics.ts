// ============================================================
// CodeWhisper PR - Analytics API Endpoints
// ============================================================

import { apiClient } from '../client';
import { extractData } from '../interceptors';

export interface TokenSavingsTrend {
  labels: string[];
  values: number[];
  period: string;
}

export interface ReviewDistribution {
  labels: string[];
  values: number[];
  percentages: number[];
}

export interface AnalyticsOverview {
  user_id: string;
  period: string;
  total_reviews: number;
  total_tokens_saved: number;
  total_original_tokens: number;
  total_optimized_tokens: number;
  average_savings_percentage: number;
  total_cost_saved: number;
  date_range: { start: string; end: string };
  generated_at: string;
}

export const analyticsApi = {
  async getTokenSavingsTrend(days: number = 7): Promise<TokenSavingsTrend> {
    const response = await apiClient.get<TokenSavingsTrend>('/analytics/token-savings', {
      params: { days },
    });
    return extractData(response);
  },

  async getReviewDistribution(): Promise<ReviewDistribution> {
    const response = await apiClient.get<ReviewDistribution>('/analytics/review-distribution');
    return extractData(response);
  },

  async getOverview(period: 'daily' | 'weekly' | 'monthly' = 'weekly'): Promise<AnalyticsOverview> {
    const response = await apiClient.get<AnalyticsOverview>('/analytics/overview', {
      params: { period },
    });
    return extractData(response);
  },
};
