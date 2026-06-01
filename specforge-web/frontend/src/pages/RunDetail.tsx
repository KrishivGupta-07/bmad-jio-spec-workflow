import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { LastRunPanel } from "@/components/LastRunPanel";
import { MessageStream } from "@/components/MessageStream";
import { TokenChart } from "@/components/TokenChart";
import { api } from "@/lib/api";
import { useRunWebSocket } from "@/lib/ws";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function RunDetail() {
  const { slug = "", runId = "" } = useParams();
  const id = Number(runId);

  const { data: run } = useQuery({
    queryKey: ["run", id],
    queryFn: () => api.getRun(id),
    enabled: Number.isFinite(id),
    refetchInterval: (q) => (q.state.data?.status === "running" ? 2000 : false),
  });

  const { events: liveEvents } = useRunWebSocket(
    run?.status === "running" ? id : null,
  );

  const isTestRun = run?.skill_name === "bmad-run-tests";
  const authError =
    (run?.auth_error ?? false) || liveEvents.some((e) => e.type === "auth_error");

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-6">
      <div>
        <Link to={`/projects/${slug}`} className="text-xs text-primary hover:underline">
          ← Dashboard
        </Link>
        <div className="mt-2 flex items-center gap-3">
          <h1 className="text-2xl font-bold">Run #{id}</h1>
          {run && <Badge variant={run.status === "success" ? "success" : run.status === "running" ? "running" : "failure"}>{run.status}</Badge>}
        </div>
        <p className="text-sm text-muted-foreground">{run?.skill_name}</p>
        {run?.claude_session_id && (
          <p className="mt-1 font-mono text-xs text-muted-foreground">
            Session: {run.claude_session_id}
          </p>
        )}
        {run?.trigger_phrase && (
          <div className="mt-3 rounded-md border bg-muted/30 px-3 py-2">
            <p className="mb-1 text-xs font-medium uppercase text-muted-foreground">Prompt</p>
            <pre className="whitespace-pre-wrap break-words font-sans text-xs">{run.trigger_phrase}</pre>
          </div>
        )}
      </div>

      {authError && (
        <div className="rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800">
          <p className="font-semibold">Claude CLI is not authenticated (401)</p>
          <p className="mt-1">
            This run failed because the Claude CLI token is missing or expired. Run{" "}
            <code className="rounded bg-red-100 px-1">claude</code> and complete the login, then
            re-run this stage. If running in Docker, the container reads{" "}
            <code className="rounded bg-red-100 px-1">~/.claude</code> from the host &mdash; mint a
            long-lived token with <code className="rounded bg-red-100 px-1">claude setup-token</code>{" "}
            so the mounted credentials work inside the container.
          </p>
        </div>
      )}

      {run?.handoff && (
        <div className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm">
          {run.handoff}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Messages</CardTitle>
        </CardHeader>
        <CardContent>
          <MessageStream messages={run?.messages ?? []} liveEvents={liveEvents} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Token timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <TokenChart calls={run?.llm_calls ?? []} />
          <div className="mt-2 text-sm text-muted-foreground">
            Total: {run?.prompt_tokens ?? 0} prompt + {run?.completion_tokens ?? 0} completion ·
            ${Number(run?.cost_usd ?? 0).toFixed(4)}
          </div>
        </CardContent>
      </Card>

      {isTestRun && (
        <Card>
          <CardHeader>
            <CardTitle>last-run.json</CardTitle>
          </CardHeader>
          <CardContent>
            <LastRunPanel lastRun={(run?.last_run as Parameters<typeof LastRunPanel>[0]["lastRun"]) ?? null} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
