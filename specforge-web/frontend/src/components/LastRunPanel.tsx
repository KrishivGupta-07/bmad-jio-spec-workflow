import { useMemo, useState } from "react";

type Failure = {
  test_id?: string;
  fr_id?: string | null;
  assertion?: string;
  message?: string;
};

type LastRun = {
  iteration?: number;
  summary?: { passed?: number; failed?: number; errored?: number };
  failures?: Failure[];
};

type Props = {
  lastRun: LastRun | null;
};

export function LastRunPanel({ lastRun }: Props) {
  const [frFilter, setFrFilter] = useState("");

  const failures = lastRun?.failures ?? [];
  const filtered = useMemo(() => {
    if (!frFilter.trim()) return failures;
    const q = frFilter.toLowerCase();
    return failures.filter((f) => (f.fr_id ?? "").toLowerCase().includes(q));
  }, [failures, frFilter]);

  const grouped = useMemo(() => {
    const map = new Map<string, Failure[]>();
    for (const f of filtered) {
      const key = f.fr_id ?? "unknown";
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(f);
    }
    return map;
  }, [filtered]);

  if (!lastRun) {
    return <p className="text-sm text-muted-foreground">No last-run.json available.</p>;
  }

  const summary = lastRun.summary ?? {};

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-2 text-sm">
        <div className="rounded border p-2">
          <div className="text-muted-foreground">Iteration</div>
          <div className="text-lg font-semibold">{lastRun.iteration ?? "—"}</div>
        </div>
        <div className="rounded border p-2">
          <div className="text-muted-foreground">Passed</div>
          <div className="text-lg font-semibold text-emerald-600">{summary.passed ?? 0}</div>
        </div>
        <div className="rounded border p-2">
          <div className="text-muted-foreground">Failed</div>
          <div className="text-lg font-semibold text-red-600">{summary.failed ?? 0}</div>
        </div>
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium">Filter by FR-ID</label>
        <input
          className="w-full rounded-md border px-2 py-1 text-sm"
          placeholder="FR-001"
          value={frFilter}
          onChange={(e) => setFrFilter(e.target.value)}
        />
      </div>

      <div className="space-y-3">
        {[...grouped.entries()].map(([frId, items]) => (
          <div key={frId} className="rounded-md border p-3">
            <h4 className="mb-2 text-sm font-semibold">{frId}</h4>
            <ul className="space-y-2 text-xs">
              {items.map((f, i) => (
                <li key={i} className="rounded bg-muted/40 p-2">
                  <div className="font-medium">{f.test_id ?? "unknown test"}</div>
                  <div className="text-muted-foreground">{f.assertion ?? f.message}</div>
                </li>
              ))}
            </ul>
          </div>
        ))}
        {filtered.length === 0 && (
          <p className="text-sm text-muted-foreground">No failures match filter.</p>
        )}
      </div>
    </div>
  );
}
