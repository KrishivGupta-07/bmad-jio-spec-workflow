import type { StageStatus } from "@/lib/api";
import { StageCard } from "./StageCard";

type Props = {
  stages: StageStatus[];
  halt: boolean;
  runningStage: string | null;
  onRunStage: (stageId: string) => void;
  onSelectRun: (runId: number) => void;
  onDevHandoff: () => void;
  showDevHandoff: boolean;
};

export function PipelineBoard({
  stages,
  halt,
  runningStage,
  onRunStage,
  onSelectRun,
  onDevHandoff,
  showDevHandoff,
}: Props) {
  return (
    <div className="space-y-4">
      {halt && (
        <div className="rounded-md border border-destructive bg-destructive/10 px-4 py-3 text-sm text-destructive">
          Iteration cap reached. Halt — surface to human.
        </div>
      )}
      {showDevHandoff && !halt && (
        <div className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm">
          <p className="mb-2">Tests failed. Dev handoff available.</p>
          <button
            type="button"
            onClick={onDevHandoff}
            className="rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground"
          >
            Run quick-dev (patches src/ only)
          </button>
        </div>
      )}
      <div className="flex gap-3 overflow-x-auto pb-2">
        {stages.map((stage) => (
          <StageCard
            key={stage.stage_id}
            stage={stage}
            disabled={
              (stage.stage_id === "run_tests" && halt) || runningStage === stage.stage_id
            }
            running={runningStage === stage.stage_id}
            onRun={() => onRunStage(stage.stage_id)}
            onSelectRun={onSelectRun}
          />
        ))}
      </div>
    </div>
  );
}
