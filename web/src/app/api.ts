/**
 * API client for communicating with the CodePilot FastAPI backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface SearchFilters {
  pathContains?: string;
  lang?: string;
}

export interface SearchResult {
  repo: string;
  path: string;
  lang: string;
  start_line: number;
  end_line: number;
  preview: string;
  score: number;
}

export interface SearchResponse {
  query: string;
  k: number;
  total_results: number;
  latency_ms: number;
  results: SearchResult[];
}

export interface IngestResponse {
  success: boolean;
  files_scanned: number;
  files_read: number;
  files_skipped: number;
  chunks_total: number;
  avg_lines_per_chunk: number;
  duration_seconds: number;
}

export interface StatusResponse {
  indexed: boolean;
  chunks: number;
  last_ingest: string | null;
  model_loaded: boolean;
  index_loaded: boolean;
}

/**
 * Search for code using semantic similarity.
 */
export async function searchCode(
  query: string,
  k: number = 5,
  filters?: SearchFilters
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    k: k.toString(),
  });

  if (filters?.pathContains) {
    params.set('pathContains', filters.pathContains);
  }
  if (filters?.lang) {
    params.set('lang', filters.lang);
  }

  const response = await fetch(`${API_BASE_URL}/search?${params}`);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Search failed: ${error}`);
  }

  return response.json();
}

/**
 * Get system status.
 */
export async function getStatus(): Promise<StatusResponse> {
  const response = await fetch(`${API_BASE_URL}/status`);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Status check failed: ${error}`);
  }

  return response.json();
}

/**
 * Trigger repository ingestion.
 */
export async function triggerIngest(
  repoPath: string,
  options?: {
    includeExts?: string[];
    excludeDirs?: string[];
    window?: number;
    overlap?: number;
  }
): Promise<IngestResponse> {
  const response = await fetch(`${API_BASE_URL}/ingest`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      repo_path: repoPath,
      ...options,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Ingestion failed: ${error}`);
  }

  return response.json();
}

/**
 * Check if the API is healthy.
 */
export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Health check failed: ${error}`);
  }

  return response.json();
}
