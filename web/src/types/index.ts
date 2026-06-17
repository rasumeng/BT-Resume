export type AppPhase = 'loading' | 'setup' | 'splash' | 'home' | 'error';

export type BackendStatus = 'disconnected' | 'connecting' | 'ready' | 'error';

export type Tab = 0 | 1 | 2 | 3;

export interface ResumeFile {
  filename: string;
  last_modified: string;
  file_size: string;
}

export interface GradeCategory {
  name: string;
  score: number;
  max_score: number;
  icon: string;
}

export interface GradeResult {
  score: number;
  label: string;
  categories: GradeCategory[];
  ats_feedback: string;
  strengths: string[];
  improvements: string[];
}

export interface PolishResult {
  polished_resume?: string;
  changes?: string[];
  polishedPdfName?: string;
}

export interface KeywordMatch {
  keyword: string;
  status: string;
}

export interface GapAnalysis {
  missing_skills: string[];
  missing_keywords: string[];
  suggestions: string[];
}

export interface AnalysisData {
  overall_confidence: number;
  category_scores: GradeCategory[];
  matches: KeywordMatch[];
  gaps: GapAnalysis;
  tailored_resume?: string;
  changes_summary?: string;
  tailoredPdfName?: string;
}

export interface FeedbackData {
  type: string;
  rating: number;
  message: string;
  name?: string;
  email?: string;
  isAnonymous?: boolean;
}

export interface AsyncState<T> {
  loading: boolean;
  data: T | null;
  error: string | null;
}

export interface ListResumesResponse {
  success: boolean;
  resumes: ResumeFile[];
}

export interface ResumeContentResponse {
  success: boolean;
  content: string;
  filename: string;
}

export interface GradeResponse {
  success: boolean;
  grade?: Record<string, unknown>;
  error?: string;
}

export interface PolishResponse {
  success: boolean;
  polished_resume?: string;
  changes?: string[];
  error?: string;
}

export interface TailorResponse {
  success: boolean;
  overall_confidence: number;
  category_scores: GradeCategory[];
  matches: KeywordMatch[];
  gaps: GapAnalysis;
  tailored_resume?: string;
  changes_summary?: string;
  error?: string;
}

export interface HealthResponse {
  status: string;
  llm_ready: boolean;
}

export interface SavePdfResponse {
  success: boolean;
  filename: string;
  path: string;
}

export interface FeedbackResponse {
  success: boolean;
  data?: { message: string };
  review?: { id: string };
  error?: string;
}

export interface ParseResponse {
  success: boolean;
  text: string;
}
