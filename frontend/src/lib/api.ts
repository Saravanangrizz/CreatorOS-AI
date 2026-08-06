import type { Generation, GenerationSettings, Project } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function getToken(): string | null {
  return localStorage.getItem("creatoros_token");
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem("creatoros_token", token);
  else localStorage.removeItem("creatoros_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // response had no JSON body — fall back to statusText
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export type StreamEvent =
  | { type: "stage_start"; agent: string; display_name: string }
  | {
      type: "stage_done";
      agent: string;
      display_name: string;
      provider: string;
      model: string;
      output: Record<string, unknown>;
      elapsed_seconds: number;
      char_count: number;
    }
  | { type: "final_package"; output: Record<string, unknown> }
  | { type: "complete"; generation_id: string; version: number }
  | { type: "error"; detail: string };

async function generateStream(
  projectId: string,
  settings: GenerationSettings,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const token = getToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/projects/${projectId}/generate/stream`, {
    method: "POST",
    headers,
    body: JSON.stringify(settings),
    signal,
  });
  if (!res.ok || !res.body) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      // no JSON body
    }
    throw new ApiError(res.status, detail);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary: number;
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      const raw = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);

      let eventType = "message";
      let dataStr = "";
      for (const line of raw.split("\n")) {
        if (line.startsWith("event:")) eventType = line.slice(6).trim();
        else if (line.startsWith("data:")) dataStr += line.slice(5).trim();
      }
      if (!dataStr) continue;
      try {
        const parsed = JSON.parse(dataStr);
        onEvent({ type: eventType, ...parsed } as StreamEvent);
      } catch {
        // ignore malformed/keep-alive frames
      }
    }
  }
}

export const api = {
  demoLogin: () =>
    request<{ access_token: string }>("/api/auth/demo-login", { method: "POST" }),
  health: () => request<{ status: string; ai_provider: string }>("/api/health"),
  listProjects: () => request<Project[]>("/api/projects"),
  createProject: (topic: string) =>
    request<Project>("/api/projects", { method: "POST", body: JSON.stringify({ topic }) }),
  generate: (projectId: string) =>
    request<Generation>(`/api/projects/${projectId}/generate`, { method: "POST" }),
  generateStream,
  listGenerations: (projectId: string) =>
    request<Generation[]>(`/api/projects/${projectId}/generations`),
  analyticsCoach: (payload: {
    ctr: string;
    watch_time: string;
    retention_notes: string;
    sub_growth: string;
  }) =>
    request<{ output: { summary: string; recommendations: string[]; reasoning: string } }>(
      "/api/projects/analytics-coach",
      { method: "POST", body: JSON.stringify(payload) }
    ),
};
