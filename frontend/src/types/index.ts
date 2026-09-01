/**
 * ReviewAI — Shared Frontend TypeScript Domain Interfaces
 * Mirrors backend Pydantic models to ensure 100% strict contract consistency.
 */

export type Language = 'python' | 'javascript' | 'typescript' | 'java' | 'cpp' | 'go' | 'rust';

export type Category = 'bug' | 'security' | 'style' | 'performance' | 'maintainability';

export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';

export type DetectionSource = 'static_analysis' | 'llm' | 'hybrid';

export type ReviewStatus = 'pending' | 'analyzing' | 'in_progress' | 'completed' | 'failed' | 'cancelled';

export interface Evidence {
  source_tool: string;
  rule_id?: string;
  line_number?: number;
  end_line?: number;
  snippet?: string;
  raw_message?: string;
}

export interface SuggestedFix {
  original_snippet: string;
  replacement_snippet: string;
  explanation?: string;
  diff?: string;
}

export interface ReviewFinding {
  id: string;
  category: Category;
  severity: Severity;
  title: string;
  description: string;
  line_number?: number;
  end_line?: number;
  column?: number;
  end_column?: number;
  code_evidence?: string;
  explanation?: string;
  recommendation?: string;
  suggested_fix?: SuggestedFix;
  confidence: number;
  confidence_level?: string;
  detection_source: DetectionSource;
  detected_by?: string[];
  rule_id?: string;
  rule_ids?: string[];
  supporting_evidence: Evidence[];
  status?: string;
}

export interface QualityScore {
  overall_score: number;
  security_score: number;
  reliability_score: number;
  performance_score: number;
  maintainability_score: number;
  style_score: number;
  category_scores: Record<string, number>;
  grade: string;
}

export interface AnalysisMetadata {
  analysis_id: string;
  language: Language;
  line_count: number;
  byte_size: number;
  review_mode: string;
  static_analysis_enabled: boolean;
  llm_enabled: boolean;
  llm_model_used?: string;
  static_only_mode: boolean;
  analyzers_executed: string[];
  stage_durations_ms: Record<string, number>;
  total_duration_ms: number;
}

export interface ReviewSummary {
  total_findings: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  info_count: number;
  category_breakdown: Record<string, number>;
  review_mode: string;
  analyzers_used: string[];
  llm_status: string;
  executive_summary: string;
}

export interface ReviewCreateRequest {
  code: string;
  language?: Language;
  filename?: string;
  context_notes?: string;
  enable_static_analysis?: boolean;
  enable_llm?: boolean;
}

export interface ReviewResponse {
  review_id: string;
  analysis_id: string;
  status: ReviewStatus;
  language: Language;
  filename: string;
  line_count: number;
  byte_size: number;
  created_at: string;
  updated_at: string;
  findings: ReviewFinding[];
  summary?: ReviewSummary;
  quality_score?: QualityScore;
  metadata?: AnalysisMetadata;
  message?: string;
}

export interface ReviewListResponse {
  items: ReviewResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
  environment: string;
  timestamp: string;
}
