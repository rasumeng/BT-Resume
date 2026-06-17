const API_BASE = '/api';

class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });

  let data: Record<string, unknown>;

  try {
    data = await res.json();
  } catch {
    throw new ApiError(`Server error (${res.status})`, res.status);
  }

  if (!data.success) {
    throw new ApiError((data.error as string) || `Request failed (${res.status})`, res.status);
  }

  return data as T;
}

export async function health(): Promise<{ status: string; llm_ready: boolean }> {
  const res = await fetch(`${API_BASE}/health`, {
    headers: { 'Content-Type': 'application/json' },
  });
  return res.json();
}

export async function uploadPdf(file: File): Promise<{ text: string }> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/extract-pdf-text`, {
    method: 'POST',
    body: formData,
  });
  const data = await res.json();
  if (!data.success) throw new ApiError(data.error || 'Failed to extract PDF text', res.status);
  return data;
}

export { request };
export { ApiError };
