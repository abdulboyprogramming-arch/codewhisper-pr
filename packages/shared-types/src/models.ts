// ============================================================
// CodeWhisper PR - Data Models
// ============================================================

// ============================================================
// User Models
// ============================================================

export interface User {
  id: string;
  email: string;
  username: string;
  fullName?: string;
  role: UserRole;
  isActive: boolean;
  isVerified: boolean;
  totalTokensSaved: number;
  totalReviewsCount: number;
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
}

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  GUEST = 'guest',
}

// ============================================================
// Review Models
// ============================================================

export interface Review {
  id: string;
  userId: string;
  repositoryUrl: string;
  repositoryName: string;
  prNumber: number;
  prTitle?: string;
  prDescription?: string;
  status: ReviewStatus;
  diffContent?: string;
  affectedFiles: AffectedFile[];
  originalTokens?: number;
  optimizedTokens?: number;
  tokensSavedPercentage?: number;
  optimizationTimeMs?: number;
  reviewOutput?: ReviewOutput;
  summary?: string;
  issuesFound: ReviewIssue[];
  modelUsed?: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  user?: User;
  tokenUsage?: TokenUsage;
}

export enum ReviewStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface AffectedFile {
  path: string;
  content?: string;
  changes: FileChange[];
}

export interface FileChange {
  type: 'added' | 'modified' | 'deleted';
  lines: number[];
  oldContent?: string;
  newContent?: string;
}

export interface ReviewOutput {
  summary: string;
  issues: ReviewIssue[];
  suggestions: string[];
  overallAssessment: Assessment;
}

export interface ReviewIssue {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  title: string;
  description: string;
  filePath: string;
  lineNumbers: number[];
  suggestion: string;
  codeExample?: string;
}

export enum Assessment {
  APPROVED = 'approved',
  CHANGES_REQUESTED = 'changes_requested',
  COMMENT = 'comment',
  DISMISSED = 'dismissed',
}

// ============================================================
// Token Usage Models
// ============================================================

export interface TokenUsage {
  id: string;
  userId: string;
  reviewId: string;
  originalTokens: number;
  optimizedTokens: number;
  tokensSaved: number;
  savingsPercentage: number;
  modelUsed: string;
  costSaved?: number;
  createdAt: string;
  review?: Review;
  user?: User;
}

// ============================================================
// Analytics Models
// ============================================================

export interface Analytics {
  id: string;
  userId: string;
  period: 'daily' | 'weekly' | 'monthly';
  totalReviews: number;
  totalTokensSaved: number;
  totalOriginalTokens: number;
  totalOptimizedTokens: number;
  averageSavingsPercentage: number;
  totalCostSaved: number;
  generatedAt: string;
  dateRange: DateRange;
}

export interface DateRange {
  start: string;
  end: string;
}

// ============================================================
// Repository Models
// ============================================================

export interface Repository {
  id: string;
  url: string;
  name: string;
  fullName: string;
  defaultBranch: string;
  userId: string;
  isPrivate: boolean;
  createdAt: string;
  updatedAt: string;
}
