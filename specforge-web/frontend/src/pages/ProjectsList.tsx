import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { useUIStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Dialog } from "@/components/ui/dialog";

export function ProjectsList() {
  const qc = useQueryClient();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const setInstallerOutput = useUIStore((s) => s.setInstallerOutput);
  const installerOutput = useUIStore((s) => s.installerOutput);

  const { data: projects = [], isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: api.listProjects,
  });

  const { data: templateStatus } = useQuery({
    queryKey: ["template-status"],
    queryFn: api.getTemplateStatus,
    refetchInterval: (query) => (query.state.data?.ready ? false : 2000),
  });

  const createMut = useMutation({
    mutationFn: () => api.createProject(name.trim()),
    onSuccess: (res) => {
      setInstallerOutput(res.installer_output);
      qc.invalidateQueries({ queryKey: ["projects"] });
      setOpen(false);
      setName("");
      navigate(`/projects/${res.project.slug}`);
    },
  });

  const canCreate = name.trim().length > 0;

  return (
    <div className="mx-auto max-w-5xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">specforge-web</h1>
          <p className="text-sm text-muted-foreground">BMAD pipeline with specforge module</p>
        </div>
        <Button onClick={() => setOpen(true)}>New project</Button>
      </div>

      {templateStatus && !templateStatus.ready && (
        <div className="mb-4 rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm">
          {templateStatus.running
            ? "Preparing shared BMAD template (one-time setup)…"
            : "BMAD template is not ready yet. New projects may fail until setup completes."}
        </div>
      )}

      {installerOutput && (
        <div className="mb-4 rounded-md border bg-muted/30 p-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium">Installer output</span>
            <Button variant="ghost" size="sm" onClick={() => setInstallerOutput(null)}>
              Dismiss
            </Button>
          </div>
          <pre className="max-h-40 overflow-auto whitespace-pre-wrap text-xs">{installerOutput}</pre>
        </div>
      )}

      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="px-4 py-2 text-left font-medium">Name</th>
              <th className="px-4 py-2 text-left font-medium">Slug</th>
              <th className="px-4 py-2 text-left font-medium">Created</th>
              <th className="px-4 py-2 text-left font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-muted-foreground">
                  Loading…
                </td>
              </tr>
            )}
            {!isLoading && projects.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-muted-foreground">
                  No projects yet. Create one to get started.
                </td>
              </tr>
            )}
            {projects.map((p) => (
              <tr key={p.id} className="border-t">
                <td className="px-4 py-2">{p.name}</td>
                <td className="px-4 py-2 font-mono text-xs">{p.slug}</td>
                <td className="px-4 py-2">{new Date(p.created_at).toLocaleString()}</td>
                <td className="px-4 py-2">
                  <Link to={`/projects/${p.slug}`} className="text-primary hover:underline">
                    Open
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Dialog open={open} onClose={() => setOpen(false)} title="New project">
        <div className="space-y-3">
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">
              Project name
            </label>
            <input
              className="w-full rounded-md border px-3 py-2 text-sm"
              placeholder="e.g. Team task board"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && canCreate) createMut.mutate();
              }}
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Create an empty project group, then add one or more instructions inside it.
              Each instruction runs the full BMAD pipeline in its own folder.
            </p>
          </div>
          <Button
            className="w-full"
            disabled={!canCreate || createMut.isPending || templateStatus?.ready === false}
            onClick={() => createMut.mutate()}
          >
            {createMut.isPending ? "Creating…" : "Create project"}
          </Button>
          {createMut.isError && (
            <p className="text-xs text-destructive">{(createMut.error as Error).message}</p>
          )}
        </div>
      </Dialog>
    </div>
  );
}
