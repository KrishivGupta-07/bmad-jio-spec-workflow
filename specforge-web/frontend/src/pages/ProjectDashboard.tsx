import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { InstructionPanel } from "@/components/InstructionPanel";
import { api } from "@/lib/api";
import { Accordion, AccordionItem } from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

function statusVariant(status: string) {
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

export function ProjectDashboard() {
  const { slug = "" } = useParams();
  const qc = useQueryClient();
  const [instructionText, setInstructionText] = useState("");

  const { data: project } = useQuery({
    queryKey: ["project", slug],
    queryFn: () => api.getProject(slug),
    enabled: !!slug,
  });

  const { data: installStatus } = useQuery({
    queryKey: ["install-status", slug],
    queryFn: () => api.getInstallStatus(slug),
    enabled: !!slug,
    refetchInterval: (query) => (query.state.data?.ready ? false : 3000),
  });

  const bmadReady = installStatus?.ready ?? true;

  const { data: instructions = [] } = useQuery({
    queryKey: ["instructions", slug],
    queryFn: () => api.listInstructions(slug),
    enabled: !!slug,
    refetchInterval: 5000,
  });

  const createInstructionMut = useMutation({
    mutationFn: (text: string) => api.createInstruction(slug, text),
    onSuccess: () => {
      setInstructionText("");
      qc.invalidateQueries({ queryKey: ["instructions", slug] });
    },
  });

  const canSubmit = instructionText.trim().length > 0 && bmadReady;

  return (
    <div className="mx-auto max-w-7xl p-6">
      <div className="mb-4">
        <Link to="/" className="text-xs text-primary hover:underline">
          ← Projects
        </Link>
        <h1 className="text-2xl font-bold">{project?.name ?? slug}</h1>
        <p className="font-mono text-xs text-muted-foreground">{project?.path}</p>
      </div>

      {!bmadReady && (
        <div className="mb-4 rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm">
          BMAD modules are still being prepared for this project. Instructions can be added
          once setup completes.
        </div>
      )}

      <div className="mb-6 rounded-lg border bg-card p-4">
        <h2 className="mb-1 text-sm font-semibold">New instruction</h2>
        <p className="mb-3 text-xs text-muted-foreground">
          Describe what to build or change. Each instruction runs the full BMAD pipeline in
          its own isolated folder — add as many as you like to this project.
        </p>
        <textarea
          className="min-h-[110px] w-full rounded-md border px-3 py-2 text-sm"
          placeholder="e.g. Add authorization to the login page so only valid users can sign in."
          value={instructionText}
          onChange={(e) => setInstructionText(e.target.value)}
        />
        <div className="mt-3 flex items-center gap-3">
          <Button
            disabled={!canSubmit || createInstructionMut.isPending}
            onClick={() => createInstructionMut.mutate(instructionText.trim())}
          >
            {createInstructionMut.isPending ? "Starting…" : "Add instruction & run"}
          </Button>
          {createInstructionMut.isError && (
            <p className="text-xs text-destructive">
              {(createInstructionMut.error as Error).message}
            </p>
          )}
        </div>
      </div>

      <h2 className="mb-3 text-sm font-semibold">
        Instructions <span className="text-muted-foreground">({instructions.length})</span>
      </h2>

      {instructions.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No instructions yet. Add one above to start the pipeline.
        </p>
      ) : (
        <Accordion type="multiple">
          {instructions.map((ins) => (
            <AccordionItem
              key={ins.id}
              value={String(ins.id)}
              trigger={
                <div className="flex items-center justify-between gap-3 pr-2">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{ins.title}</p>
                    <p className="truncate text-xs text-muted-foreground">
                      {ins.is_default ? "Adopted legacy artifacts" : ins.instruction_text}
                    </p>
                  </div>
                  <div className="flex flex-shrink-0 items-center gap-2">
                    <Badge variant={statusVariant(ins.status)}>{ins.status}</Badge>
                    <span className="hidden text-xs text-muted-foreground sm:inline">
                      {new Date(ins.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              }
            >
              <InstructionPanel
                instructionId={ins.id}
                projectSlug={slug}
                bmadReady={bmadReady}
              />
            </AccordionItem>
          ))}
        </Accordion>
      )}
    </div>
  );
}
