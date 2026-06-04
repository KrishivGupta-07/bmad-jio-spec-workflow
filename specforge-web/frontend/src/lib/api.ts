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
  instruction_id: number | null;
  skill_name: string;
  trigger_phrase: string;
  status: string;
  started_at: string | null;
  ended_at: string | null;
  iteration: number | null;
  claude_session_id: string | null;
};

export type Instruction = {
  id: number;
  project_id: number;
  slug: string;
  title: string;
  instruction_text: string;
  path: string;
  is_default: boolean;
  status: string;
  created_at: string;
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

export type Artifact = {
  id: number;
  project_id: number;
  instruction_id: number | null;
  kind: string;
  path: string;
  sha256: string;
  updated_at: string;
  content?: string;
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
  instruction_id: number | null;
  stages: StageStatus[];
  latest_test_run: TestRun | null;
  halt: boolean;
  auto_advance: boolean;
};

export type ProjectMetrics = {
  project_slug: string;
  instruction_id: number | null;
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

export type InstructionDetail = Instruction & {
  project_slug: string;
  project_name: string;
};

export const api = {
  listProjects: () => request<Project[]>("/projects"),
  createProject: (name: string) =>
    request<{ project: Project; installer_output: string }>("/projects", {
      method: "POST",
      body: JSON.stringify({ name }),
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

  // Instructions (one prompt -> its own dir + pipeline within a project group)
  listInstructions: (slug: string) =>
    request<Instruction[]>(`/projects/${slug}/instructions`),
  createInstruction: (slug: string, text: string) =>
    request<Instruction>(`/projects/${slug}/instructions`, {
      method: "POST",
      body: JSON.stringify({ text }),
    }),
  getInstruction: (instructionId: number) =>
    request<InstructionDetail>(`/instructions/${instructionId}`),
  advanceInstruction: (instructionId: number) =>
    request<InstructionDetail>(`/instructions/${instructionId}/advance`, {
      method: "POST",
    }),
  startRun: (instructionId: number, stage: string) =>
    request<Run>(`/instructions/${instructionId}/runs`, {
      method: "POST",
      body: JSON.stringify({ stage }),
    }),
  getPipeline: (instructionId: number) =>
    request<PipelineStatus>(`/instructions/${instructionId}/pipeline`),
  getMetrics: (instructionId: number) =>
    request<ProjectMetrics>(`/instructions/${instructionId}/metrics`),
  listArtifacts: (instructionId: number) =>
    request<Artifact[]>(`/instructions/${instructionId}/artifacts`),
  readArtifact: (instructionId: number, kind: string) =>
    request<Artifact>(`/instructions/${instructionId}/artifacts/${kind}`),

  getRun: (runId: number) => request<RunDetail>(`/runs/${runId}`),
  getLastRun: (instructionId: number) =>
    request<Record<string, unknown>>(`/instructions/${instructionId}/last-run`),
  listFailures: (instructionId: number) =>
    request<{ fr_id: string | null; test_name: string; message: string }[]>(
      `/instructions/${instructionId}/failures`,
    ),
};

export function vscodeUri(path: string) {
  return `vscode://file/${path}`;
}
