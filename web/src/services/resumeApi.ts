import { request, uploadPdf } from './api';
import type { AnalysisData, ResumeFile, ListResumesResponse, ResumeContentResponse } from '../types';

function normalizeResume(item: unknown): ResumeFile {
  const r = item as Partial<ResumeFile> & {
    name?: string;
    size?: number | string;
    modified?: number | string;
  };

  const rawModified = r.last_modified ?? r.modified ?? '';
  const modified = typeof rawModified === 'number'
    ? new Date(rawModified * 1000).toISOString()
    : String(rawModified);

  const rawSize = r.file_size ?? r.size ?? '0 KB';
  const fileSize = typeof rawSize === 'number' ? `${Math.max(0, Math.round(rawSize / 1024))} KB` : String(rawSize);

  return {
    filename: r.filename ?? r.name ?? 'Unknown.pdf',
    last_modified: modified,
    file_size: fileSize,
  };
}

export async function listResumes(): Promise<ResumeFile[]> {
  const response = await request<ListResumesResponse>('/list-resumes');
  return Array.isArray(response.resumes)
    ? response.resumes.map(normalizeResume)
    : [];
}

export async function getResume(filename: string): Promise<string> {
  const response = await request<ResumeContentResponse>(
    `/get-resume?filename=${encodeURIComponent(filename)}`,
  );
  return response.content ?? '';
}

export async function deleteResume(filename: string): Promise<void> {
  await request(`/delete-resume?filename=${encodeURIComponent(filename)}`, {
    method: 'DELETE',
  });
}

export async function updateResume(filename: string, content: string): Promise<void> {
  await request('/update-resume', {
    method: 'POST',
    body: JSON.stringify({ filename, content }),
  });
}

export async function extractPdfText(file: File): Promise<string> {
  const result = await uploadPdf(file);
  return result.text;
}

export async function saveTextPdf(filename: string, textContent: string, useTemp = true): Promise<{ filename: string; path: string }> {
  const response = await request<{ success: boolean; filename: string; path: string }>(
    '/save-text-pdf',
    {
      method: 'POST',
      body: JSON.stringify({ filename, text_content: textContent, use_temp: useTemp }),
    },
  );
  return { filename: response.filename, path: response.path };
}

export async function parseAndCacheResume(resumeText: string, filename?: string): Promise<AnalysisData> {
  const response = await request<{ success: boolean; parsed_resume: AnalysisData }>(
    '/parse-resume',
    {
      method: 'POST',
      body: JSON.stringify({ resume_text: resumeText, filename }),
    },
  );

  return response.parsed_resume;
}

export async function uploadResume(file: File): Promise<{ filename: string; path: string; parsed_cached: boolean }> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch('/api/upload-resume', {
    method: 'POST',
    body: formData,
  });

  const data = await res.json();
  if (!data.success) {
    throw new Error(data.error || 'Failed to upload resume');
  }

  return data;
}
