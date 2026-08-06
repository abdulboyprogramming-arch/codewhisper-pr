// ============================================================
// CodeWhisper PR - Utility Types
// ============================================================

// ============================================================
// Pagination Types
// ============================================================

export interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

// ============================================================
// Filter Types
// ============================================================

export interface ReviewFilter {
  status?: ReviewStatus[];
  category?: string[];
  severity?: string[];
  dateRange?: DateRange;
  search?: string;
}

export type { ReviewStatus } from './models';

export interface DateRange {
  start?: string;
  end?: string;
}

// ============================================================
// Webhook Types
// ============================================================

export interface WebhookEvent {
  id: string;
  type: WebhookType;
  payload: any;
  timestamp: string;
  processed: boolean;
}

export enum WebhookType {
  PR_CREATED = 'pr_created',
  PR_UPDATED = 'pr_updated',
  PR_MERGED = 'pr_merged',
  REVIEW_REQUESTED = 'review_requested',
}

// ============================================================
// Configuration Types
// ============================================================

export interface AppConfig {
  appName: string;
  version: string;
  environment: 'development' | 'staging' | 'production';
  debug: boolean;
  logLevel: LogLevel;
  features: FeatureFlags;
  limits: RateLimits;
}

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface FeatureFlags {
  enableAnalytics: boolean;
  enableCaching: boolean;
  enableBackgroundProcessing: boolean;
  enableEmailNotifications: boolean;
}

export interface RateLimits {
  maxRequestsPerMinute: number;
  maxConcurrentReviews: number;
  maxFileSizeMB: number;
}
