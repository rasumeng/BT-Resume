import { request } from './api';
import type {
  GradeResult,
  GradeResponse,
  PolishResult,
  PolishResponse,
  AnalysisData,
  TailorResponse,
  GradeCategory,
  KeywordMatch,
} from '../types';

const GRADE_CATEGORY_ICONS: Record<string, string> = {
  'ATS Compatibility': '🤖',
  'Structure & Sections': '📋',
  'Bullet Quality': '🎯',
  'Content Strength': '💪',
  'Keyword Optimization': '🔑',
};

function getScoreLabel(score: number): string {
  if (score >= 85) return 'Excellent';
  if (score >= 70) return 'Good';
  if (score >= 60) return 'Fair';
  return 'Needs Work';
}

export async function gradeResume(resumeText: string, filename?: string): Promise<GradeResult> {
  const body: Record<string, string> = { resume_text: resumeText };
  if (filename) {
    body.filename = filename;
    body.resume_text = '';
  }
  const response = await request<GradeResponse>('/grade-resume', {
    method: 'POST',
    body: JSON.stringify(body),
  });

  if (!response.grade) {
    throw new Error('No grade data returned');
  }

  const g = response.grade as Record<string, unknown>;

  const dimensionMap: { key: string; name: string; maxScore: number }[] = [
    { key: 'atsScore', name: 'ATS Compatibility', maxScore: 10 },
    { key: 'sectionsScore', name: 'Structure & Sections', maxScore: 10 },
    { key: 'bulletsScore', name: 'Bullet Quality', maxScore: 10 },
    { key: 'contentScore', name: 'Content Strength', maxScore: 10 },
    { key: 'keywordsScore', name: 'Keyword Optimization', maxScore: 10 },
  ];

  const categories: GradeCategory[] = dimensionMap.map((d) => ({
    name: d.name,
    score: (g[d.key] as number) ?? 0,
    max_score: d.maxScore,
    icon: GRADE_CATEGORY_ICONS[d.name] ?? '📊',
  }));

  const overallScore = (g.score as number) ?? 0;

  return {
    score: overallScore,
    label: getScoreLabel(overallScore),
    categories,
    ats_feedback: (g.atsFeedback as string) ?? (g.ats_feedback as string) ?? '',
    strengths: Array.isArray(g.strengths) ? (g.strengths as string[]) : [],
    improvements: Array.isArray(g.improvements) ? (g.improvements as string[]) : [],
  };
}

export async function polishResume(
  resumeText: string,
  intensity: string = 'medium',
): Promise<PolishResult> {
  const response = await request<PolishResponse>('/polish-resume', {
    method: 'POST',
    body: JSON.stringify({ resume_text: resumeText, intensity }),
  });

  return {
    polished_resume: response.polished_resume ?? undefined,
    changes: Array.isArray(response.changes) ? response.changes : undefined,
  };
}

export async function analyzeFit(
  resumeText: string,
  jobDescription: string,
  options?: { jobPosition?: string; companyName?: string },
): Promise<AnalysisData> {
  const response = await request<TailorResponse>('/analyze-fit', {
    method: 'POST',
    body: JSON.stringify({
      resume_text: resumeText,
      job_description: jobDescription,
      job_position: options?.jobPosition ?? '',
      company_name: options?.companyName ?? '',
    }),
  });

  return normalizeTailorResponse(response);
}

export async function tailorResume(
  resumeText: string,
  jobDescription: string,
  intensity: string = 'medium',
  options?: { jobPosition?: string; companyName?: string },
): Promise<AnalysisData> {
  const response = await request<TailorResponse>('/tailor-resume', {
    method: 'POST',
    body: JSON.stringify({
      resume_text: resumeText,
      job_description: jobDescription,
      intensity,
      job_position: options?.jobPosition ?? '',
      company_name: options?.companyName ?? '',
    }),
  });

  return normalizeTailorResponse(response);
}

function normalizeCategoryScore(cs: Record<string, unknown>): GradeCategory {
  const categoryName = (cs.category as string) ?? (cs.name as string) ?? '';
  return {
    name: categoryName,
    score: (cs.score as number) ?? 0,
    max_score: (cs.max_score as number) ?? (cs.maxScore as number) ?? 100,
    icon: GRADE_CATEGORY_ICONS[categoryName] ?? '📊',
  };
}

function normalizeMatch(m: Record<string, unknown>): KeywordMatch {
  const relevance = (m.relevance as number) ?? 50;
  let status: string;
  if (relevance >= 80) status = 'matched';
  else if (relevance >= 50) status = 'partial';
  else status = 'weak';
  return {
    keyword: (m.keyword as string) ?? '',
    status,
  };
}

function normalizeTailorResponse(response: TailorResponse): AnalysisData {
  const rawCategoryScores = response.category_scores as unknown as Record<string, unknown>[] | undefined;
  const rawMatches = response.matches as unknown as Record<string, unknown>[] | undefined;

  return {
    overall_confidence: response.overall_confidence ?? 0,
    category_scores: Array.isArray(rawCategoryScores)
      ? rawCategoryScores.map(normalizeCategoryScore)
      : [],
    matches: Array.isArray(rawMatches)
      ? rawMatches.map(normalizeMatch)
      : [],
    gaps: {
      missing_skills: Array.isArray(response.gaps?.missing_skills) ? response.gaps.missing_skills : [],
      missing_keywords: Array.isArray(response.gaps?.missing_keywords) ? response.gaps.missing_keywords : [],
      suggestions: Array.isArray(response.gaps?.suggestions) ? response.gaps.suggestions : [],
    },
    tailored_resume: response.tailored_resume ?? undefined,
    changes_summary: response.changes_summary ?? undefined,
  };
}
