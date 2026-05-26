import type { StageStatus } from "@/lib/api";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

type Props = {
  stage: StageStatus;
  disabled?: boolean;
  running?: boolean;
  onRun: () => void;
  onSelectRun: (runId: number) => void;
};

function statusVariant(status: string | undefined) {
  switch (status) {
    case "success":
      return "success" as const;
    case "failure":
      return "failure" as const;
    case "running":
      return "running" as const;
    case "halted":
      return "halted" as const;
    default:
      return "pending" as const;
  }
}

export function StageCard({ stage, disabled, running, onRun, onSelectRun }: Props) {
  const last = stage.last_run;
  const status = running ? "running" : last?.status;

  return (
    <Card className="min-w-[200px] flex-shrink-0">
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle>{stage.label}</CardTitle>
          <Badge variant={statusVariant(status)}>{status ?? "idle"}</Badge>
        </div>
        <p className="text-xs text-muted-foreground">{stage.skill_name}</p>
        <p className="text-[10px] text-muted-foreground">{stage.module}</p>
      </CardHeader>
      <CardContent className="space-y-2">
        {last?.started_at && (
          <p className="text-xs text-muted-foreground">
            Last: {new Date(last.started_at).toLocaleString()}
          </p>
        )}
        <p className="text-xs">
          {stage.prompt_tokens + stage.completion_tokens} tokens · ${Number(stage.cost_usd).toFixed(4)}
        </p>
        <div className="flex gap-2">
          <Button size="sm" disabled={disabled || running} onClick={onRun}>
            {running ? "Running…" : "Run"}
          </Button>
          {last && (
            <Button size="sm" variant="outline" onClick={() => onSelectRun(last.id)}>
              View
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
