import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArtifactViewer } from "@/components/ArtifactViewer";
import { MessageStream } from "@/components/MessageStream";
import { PipelineBoard } from "@/components/PipelineBoard";
import { TokenChart } from "@/components/TokenChart";
import { api } from "@/lib/api";
import { useUIStore } from "@/lib/store";
import { useRunWebSocket } from "@/lib/ws";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ProjectDashboard() {
  const { slug = "" } = useParams();
  const qc = useQueryClient();
  const autoAdvance = useUIStore((s) => s.autoAdvance);
  const setAutoAdvance = useUIStore((s) => s.setAutoAdvance);
  const selectedArtifactKind = useUIStore((s) => s.selectedArtifactKind);
  const setSelectedArtifactKind = useUIStore((s) => s.setSelectedArtifactKind);
  const [activeRunId, setActiveRunId] = useState<number | null>(null);
  const [runningStage, setRunningStage] = useState<string | null>(null);

  const { data: project } = useQuery({
    queryKey: ["project", slug],
    queryFn: () => api.getProject(slug),
    enabled: !!slug,
  });

  const { data: pipeline, refetch: refetchPipeline } = useQuery({
    queryKey: ["pipeline", slug],
    queryFn: () => api.getPipeline(slug),
    enabled: !!slug,
    refetchInterval: runningStage ? 3000 : false,
  });

  const { data: metrics } = useQuery({
    queryKey: ["metrics", slug],
    queryFn: () => api.getMetrics(slug),
    enabled: !!slug,
  });

  const { data: artifacts = [] } = useQuery({
    queryKey: ["artifacts", slug],
    queryFn: () => api.listArtifacts(slug),
    enabled: !!slug,
  });

  const { data: artifactContent } = useQuery({
    queryKey: ["artifact", slug, selectedArtifactKind],
    queryFn: () => api.readArtifact(slug, selectedArtifactKind!),
    enabled: !!slug && !!selectedArtifactKind,
  });

  const { data: activeRun } = useQuery({
    queryKey: ["run", activeRunId],
    queryFn: () => api.getRun(activeRunId!),
    enabled: !!activeRunId,
    refetchInterval: runningStage ? 2000 : false,
  });

  const { events: liveEvents } = useRunWebSocket(activeRunId, (event) => {
    if (event.type === "run_complete") {
      setRunningStage(null);
      refetchPipeline();
      qc.invalidateQueries({ queryKey: ["metrics", slug] });
      qc.invalidateQueries({ queryKey: ["artifacts", slug] });
      qc.invalidateQueries({ queryKey: ["run", activeRunId] });
    }
  });

  const startRunMut = useMutation({
    mutationFn: (stage: string) => api.startRun(slug, stage),
    onSuccess: (run) => {
      setActiveRunId(run.id);
      setRunningStage(
        pipeline?.stages.find((s) => s.skill_name === run.skill_name)?.stage_id ?? null,
      );
    },
  });

  const runStage = useCallback(
    (stageId: string) => {
      startRunMut.mutate(stageId);
    },
    [startRunMut],
  );

  useEffect(() => {
    if (!autoAdvance || !pipeline || runningStage) return;
    const lastTest = pipeline.latest_test_run;
    if (lastTest && lastTest.failed > 0 && lastTest.iteration < 5) {
      // User must explicitly click dev handoff — auto-advance only chains run_tests retry after quick_dev
      return;
    }
  }, [autoAdvance, pipeline, runningStage]);

  const showDevHandoff =
    !!pipeline?.latest_test_run &&
    pipeline.latest_test_run.failed > 0 &&
    (pipeline.latest_test_run.iteration ?? 0) < 5;

  return (
    <div className="mx-auto max-w-7xl p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <Link to="/" className="text-xs text-primary hover:underline">
            ← Projects
          </Link>
          <h1 className="text-2xl font-bold">{project?.name ?? slug}</h1>
          <p className="font-mono text-xs text-muted-foreground">{project?.path}</p>
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={autoAdvance}
            onChange={(e) => setAutoAdvance(e.target.checked)}
          />
          Auto-advance (off by default)
        </label>
      </div>

      <PipelineBoard
        stages={pipeline?.stages ?? []}
        halt={pipeline?.halt ?? false}
        runningStage={runningStage}
        onRunStage={runStage}
        onSelectRun={(id) => setActiveRunId(id)}
        onDevHandoff={() => runStage("quick_dev")}
        showDevHandoff={showDevHandoff}
      />

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Live stream {activeRunId ? `#${activeRunId}` : ""}</CardTitle>
            </CardHeader>
            <CardContent>
              {activeRunId ? (
                <>
                  <MessageStream messages={activeRun?.messages ?? []} liveEvents={liveEvents} />
                  {activeRun && (
                    <div className="mt-3">
                      <Link to={`/projects/${slug}/runs/${activeRunId}`} className="text-xs text-primary">
                        Open run detail →
                      </Link>
                    </div>
                  )}
                </>
              ) : (
                <p className="text-sm text-muted-foreground">Run a stage to see live output.</p>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1 text-sm">
              <p>Runs: {metrics?.total_runs ?? 0}</p>
              <p>Tokens: {(metrics?.prompt_tokens ?? 0) + (metrics?.completion_tokens ?? 0)}</p>
              <p>Cost: ${Number(metrics?.cost_usd ?? 0).toFixed(4)}</p>
              <TokenChart calls={activeRun?.llm_calls ?? []} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Artifacts</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {artifacts.length === 0 && (
                <p className="text-sm text-muted-foreground">No artifacts yet.</p>
              )}
              {artifacts.map((a) => (
                <Button
                  key={a.id}
                  variant={selectedArtifactKind === a.kind ? "default" : "outline"}
                  size="sm"
                  className="mr-2"
                  onClick={() => setSelectedArtifactKind(a.kind)}
                >
                  {a.kind}
                </Button>
              ))}
              {artifactContent?.content && selectedArtifactKind && (
                <div className="mt-4">
                  <ArtifactViewer
                    content={artifactContent.content}
                    path={artifactContent.path}
                    kind={selectedArtifactKind}
                  />
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
