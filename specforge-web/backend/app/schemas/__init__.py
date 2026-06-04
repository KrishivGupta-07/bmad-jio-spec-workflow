from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    # Optional: projects are now empty groups; instructions drive the pipeline.
    product_description: str | None = None


class ProjectUpdate(BaseModel):
    product_description: str


class InstructionCreate(BaseModel):
    text: str


class InstructionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    slug: str
    title: str
    instruction_text: str
    path: str
    is_default: bool
    status: str
    created_at: datetime


class InstructionDetailOut(InstructionOut):
    project_slug: str
    project_name: str


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    path: str
    product_description: str | None = None
    created_at: datetime


class ProjectCreateResult(BaseModel):
    project: ProjectOut
    installer_output: str


class InstallStatus(BaseModel):
    ready: bool
    running: bool
    log: str | None = None


class RunCreate(BaseModel):
    project_slug: str
    stage: str


class StageStart(BaseModel):
    stage: str


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    instruction_id: int | None = None
    skill_name: str
    trigger_phrase: str
    status: str
    started_at: datetime | None
    ended_at: datetime | None
    iteration: int | None
    claude_session_id: str | None


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int
    role: str
    content: str
    ts: datetime


class LLMCallOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: Decimal
    latency_ms: int | None
    ts: datetime


class RunDetailOut(RunOut):
    messages_count: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: Decimal = Decimal("0")
    messages: list[MessageOut] = []
    llm_calls: list[LLMCallOut] = []
    handoff: str | None = None
    last_run: dict[str, Any] | None = None
    auth_error: bool = False


class ArtifactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    kind: str
    path: str
    sha256: str
    updated_at: datetime
    content: str | None = None


class TestRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    iteration: int
    passed: int
    failed: int
    last_run_json_path: str
    ts: datetime


class ProjectMetrics(BaseModel):
    project_slug: str
    instruction_id: int | None = None
    total_runs: int
    prompt_tokens: int
    completion_tokens: int
    cost_usd: Decimal
    runs_by_stage: dict[str, int]


class StageStatus(BaseModel):
    stage_id: str
    skill_name: str
    module: str
    label: str
    trigger_phrase: str
    last_run: RunOut | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: Decimal = Decimal("0")


class PipelineStatus(BaseModel):
    project_slug: str
    instruction_id: int | None = None
    stages: list[StageStatus]
    latest_test_run: TestRunOut | None = None
    halt: bool = False
    auto_advance: bool = False


class FailureItem(BaseModel):
    fr_id: str | None
    test_name: str
    message: str
