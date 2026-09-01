/**
 * ReviewAI — Typed HTTP API Client
 * Centralizes all backend API communication, error serialization, and request tracking.
 */

import {
  HealthResponse,
  ReviewCreateRequest,
  ReviewListResponse,
  ReviewResponse,
} from '../types';

const API_BASE = (import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api/v1` : '/api/v1');

export class ApiError extends Error {
  public status: number;
  public code?: string;
  public details?: any;

  constructor(message: string, status: number, code?: string, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorData: any = {};
    try {
      errorData = await res.json();
    } catch {
      // Non-JSON error payload
    }

    const err = errorData?.error || {};
    const message = err.message || errorData.detail || `HTTP error ${res.status}: ${res.statusText}`;
    throw new ApiError(message, res.status, err.code, err.details);
  }

  return res.json();
}

export const apiService = {
  /** Check backend health status */
  async checkHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE}/health`, {
      headers: { 'Accept': 'application/json' },
    });
    return handleResponse<HealthResponse>(res);
  },

  /** Submit new code review job */
  async submitReview(payload: ReviewCreateRequest): Promise<ReviewResponse> {
    const res = await fetch(`${API_BASE}/reviews`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        code: payload.code,
        language: payload.language || 'python',
        filename: payload.filename || 'submission.py',
        context_notes: payload.context_notes,
        enable_static_analysis: payload.enable_static_analysis ?? true,
        enable_llm: payload.enable_llm ?? true,
      }),
    });
    return handleResponse<ReviewResponse>(res);
  },

  /** Fetch a specific review by UUID */
  async getReview(reviewId: string): Promise<ReviewResponse> {
    const res = await fetch(`${API_BASE}/reviews/${encodeURIComponent(reviewId)}`, {
      headers: { 'Accept': 'application/json' },
    });
    return handleResponse<ReviewResponse>(res);
  },

  /** Retrieve paginated review history */
  async listReviews(page = 1, pageSize = 20): Promise<ReviewListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    const res = await fetch(`${API_BASE}/reviews?${params.toString()}`, {
      headers: { 'Accept': 'application/json' },
    });
    return handleResponse<ReviewListResponse>(res);
  },

  /** Delete a review record */
  async deleteReview(reviewId: string): Promise<boolean> {
    const res = await fetch(`${API_BASE}/reviews/${encodeURIComponent(reviewId)}`, {
      method: 'DELETE',
    });
    if (!res.ok) {
      throw new ApiError(`Failed to delete review: ${res.statusText}`, res.status);
    }
    return true;
  },
};
