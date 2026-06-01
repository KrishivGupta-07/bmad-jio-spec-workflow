export type Project = {
  id: number;
  name: string;
  slug: string;
  path: string;
  product_description: string | null;
  created_at: string;
};

export type Run = {
  id: number;
  project_id: number;
  skill_name: string;
  trigger_phrase: string;
  status: string;
  started_at: string | null;
  ended_at: string | null;
  iteration: number | null;
  claude_session_id: string | null;
};

export type Message = {
  id: number;
  run_id: number;
  role: string;
  content: string;
  ts: string;
};

export type LLMCall = {
  id: number;
  run_id: number;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  cost_usd: string;
  latency_ms: number | null;
  ts: string;
};

export type RunDetail = Run & {
  messages_count: number;
  prompt_tokens: number;
  completion_tokens: number;
  cost_usd: string;
  messages: Message[];
  llm_calls: LLMCall[];
  handoff: string | null;
  last_run: Record<string, unknown> | null;
  auth_error: boolean;
};

export type Artifact = {
  id: number;
  project_id: number;
  kind: string;
  path: string;
  sha256: string;
  updated_at: string;
  content?: string;
};

export type StageStatus = {
  stage_id: string;
  skill_name: string;
  module: string;
  label: string;
  trigger_phrase: string;
  last_run: Run | null;
  prompt_tokens: number;
  completion_tokens: number;
  cost_usd: string;
};

export type TestRun = {
  id: number;
  project_id: number;
  iteration: number;
  passed: number;
  failed: number;
  last_run_json_path: string;
  ts: string;
};

export type PipelineStatus = {
  project_slug: string;
  stages: StageStatus[];
  latest_test_run: TestRun | null;
  halt: boolean;
  auto_advance: boolean;
};

export type ProjectMetrics = {
  project_slug: string;
  total_runs: number;
  prompt_tokens: number;
  completion_tokens: number;
  cost_usd: string;
  runs_by_stage: Record<string, number>;
};

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

export const api = {
  listProjects: () => request<Project[]>("/projects"),
  createProject: (name: string, productDescription: string) =>
    request<{ project: Project; installer_output: string }>("/projects", {
      method: "POST",
      body: JSON.stringify({ name, product_description: productDescription }),
    }),
  updateProject: (slug: string, productDescription: string) =>
    request<Project>(`/projects/${slug}`, {
      method: "PATCH",
      body: JSON.stringify({ product_description: productDescription }),
    }),
  getInstallStatus: (slug: string) =>
    request<{ ready: boolean; running: boolean; log: string | null }>(
      `/projects/${slug}/install-status`,
    ),
  getTemplateStatus: () =>
    request<{ ready: boolean; running: boolean; log: string | null }>(
      "/projects/template/status",
    ),
  getProject: (slug: string) => request<Project>(`/projects/${slug}`),
  startRun: (project_slug: string, stage: string) =>
    request<Run>("/runs", {
      method: "POST",
      body: JSON.stringify({ project_slug, stage }),
    }),
  getRun: (runId: number) => request<RunDetail>(`/runs/${runId}`),
  getPipeline: (slug: string) => request<PipelineStatus>(`/projects/${slug}/pipeline`),
  getMetrics: (slug: string) => request<ProjectMetrics>(`/metrics/projects/${slug}`),
  listArtifacts: (slug: string) => request<Artifact[]>(`/projects/${slug}/artifacts`),
  readArtifact: (slug: string, kind: string) =>
    request<Artifact>(`/projects/${slug}/artifacts/${kind}`),
  getLastRun: (slug: string) => request<Record<string, unknown>>(`/projects/${slug}/last-run`),
  listFailures: (slug: string) =>
    request<{ fr_id: string | null; test_name: string; message: string }[]>(
      `/projects/${slug}/failures`,
    ),
};

export function vscodeUri(path: string) {
  return `vscode://file/${path}`;
}
