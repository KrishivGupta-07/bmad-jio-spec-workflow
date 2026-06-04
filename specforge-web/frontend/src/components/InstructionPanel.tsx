import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ArtifactViewer } from "@/components/ArtifactViewer";
import { MessageStream } from "@/components/MessageStream";
import { PipelineBoard } from "@/components/PipelineBoard";
import { api } from "@/lib/api";
import { useRunWebSocket } from "@/lib/ws";
import { Button } from "@/components/ui/button";

type Props = {
  instructionId: number;
  projectSlug: string;
  bmadReady: boolean;
};

export function InstructionPanel({ instructionId, projectSlug, bmadReady }: Props) {
  const qc = useQueryClient();
  const [activeRunId, setActiveRunId] = useState<number | null>(null);
  const [selectedKind, setSelectedKind] = useState<string | null>(null);

  const { data: pipeline, refetch: refetchPipeline } = useQuery({
    queryKey: ["ins-pipeline", instructionId],
    queryFn: () => api.getPipeline(instructionId),
    refetchInterval: 4000,
  });

  const { data: metrics } = useQuery({
    queryKey: ["ins-metrics", instructionId],
    queryFn: () => api.getMetrics(instructionId),
    refetchInterval: 8000,
  });

  const { data: artifacts = [] } = useQuery({
    queryKey: ["ins-artifacts", instructionId],
    queryFn: () => api.listArtifacts(instructionId),
    refetchInterval: 8000,
  });

  const { data: artifactContent } = useQuery({
    queryKey: ["ins-artifact", instructionId, selectedKind],
    queryFn: () => api.readArtifact(instructionId, selectedKind!),
    enabled: !!selectedKind,
  });

  // Which stage (if any) is currently running, derived from pipeline state.
  const runningStage = useMemo(() => {
    const s = pipeline?.stages.find((st) => st.last_run?.status === "running");
    return s?.stage_id ?? null;
  }, [pipeline]);

  // Auto-follow the running stage's run in the live stream.
  useEffect(() => {
    if (runningStage && !activeRunId) {
      const run = pipeline?.stages.find((s) => s.stage_id === runningStage)?.last_run;
      if (run) setActiveRunId(run.id);
    }
  }, [runningStage, activeRunId, pipeline]);

  const { data: activeRun } = useQuery({
    queryKey: ["run", activeRunId],
    queryFn: () => api.getRun(activeRunId!),
    enabled: !!activeRunId,
    refetchInterval: (q) => (q.state.data?.status === "running" ? 2000 : false),
  });

  const { events: liveEvents } = useRunWebSocket(
    activeRun?.status === "running" ? activeRunId : null,
    (event) => {
      if (event.type === "run_complete") {
        refetchPipeline();
        qc.invalidateQueries({ queryKey: ["ins-artifacts", instructionId] });
        qc.invalidateQueries({ queryKey: ["ins-metrics", instructionId] });
      }
    },
  );

  const startRunMut = useMutation({
    mutationFn: (stage: string) => api.startRun(instructionId, stage),
    onSuccess: (run) => {
      setActiveRunId(run.id);
      refetchPipeline();
    },
  });

  const advanceMut = useMutation({
    mutationFn: () => api.advanceInstruction(instructionId),
    onSuccess: () => refetchPipeline(),
  });

  const showDevHandoff =
    !!pipeline?.latest_test_run &&
    pipeline.latest_test_run.failed > 0 &&
    (pipeline.latest_test_run.iteration ?? 0) < 5;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <Button
          size="sm"
          variant="outline"
          disabled={!bmadReady || advanceMut.isPending}
          onClick={() => advanceMut.mutate()}
        >
          {advanceMut.isPending ? "Resuming…" : "Resume / continue pipeline"}
        </Button>
        <span className="text-xs text-muted-foreground">
          Runs the full pipeline, skipping stages whose artifacts already exist.
        </span>
      </div>

      <PipelineBoard
        stages={pipeline?.stages ?? []}
        halt={pipeline?.halt ?? false}
        runningStage={runningStage}
        installNotReady={!bmadReady}
        onRunStage={(stage) => startRunMut.mutate(stage)}
        onSelectRun={(id) => setActiveRunId(id)}
        onDevHandoff={() => startRunMut.mutate("quick_dev")}
        showDevHandoff={showDevHandoff}
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="space-y-2 lg:col-span-2">
          <div className="rounded-lg border">
            <div className="flex items-center justify-between border-b px-3 py-2">
              <span className="text-sm font-medium">
                Live stream {activeRunId ? `#${activeRunId}` : ""}
              </span>
              {activeRunId && (
                <Link
                  to={`/projects/${projectSlug}/instructions/${instructionId}/runs/${activeRunId}`}
                  className="text-xs text-primary hover:underline"
                >
                  Open run detail →
                </Link>
              )}
            </div>
            <div className="p-3">
              {activeRunId ? (
                <MessageStream messages={activeRun?.messages ?? []} liveEvents={liveEvents} />
              ) : (
                <p className="text-sm text-muted-foreground">
                  Select a stage run to see live output.
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-lg border p-3 text-sm">
            <p className="mb-1 font-medium">Metrics</p>
            <p>Runs: {metrics?.total_runs ?? 0}</p>
            <p>
              Tokens: {(metrics?.prompt_tokens ?? 0) + (metrics?.completion_tokens ?? 0)}
            </p>
            <p>Cost: ${Number(metrics?.cost_usd ?? 0).toFixed(4)}</p>
          </div>

          <div className="rounded-lg border p-3">
            <p className="mb-2 text-sm font-medium">Artifacts</p>
            {artifacts.length === 0 && (
              <p className="text-sm text-muted-foreground">No artifacts yet.</p>
            )}
            <div className="flex flex-wrap gap-2">
              {artifacts.map((a) => (
                <Button
                  key={a.id}
                  variant={selectedKind === a.kind ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedKind(a.kind)}
                >
                  {a.kind}
                </Button>
              ))}
            </div>
            {artifactContent?.content && selectedKind && (
              <div className="mt-3">
                <ArtifactViewer
                  content={artifactContent.content}
                  path={artifactContent.path}
                  kind={selectedKind}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
