import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { vscodeUri } from "@/lib/api";

type Props = {
  content: string;
  path?: string;
  kind: string;
};

export function ArtifactViewer({ content, path, kind }: Props) {
  const isMarkdown = kind !== "last_run";

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold capitalize">{kind.replace("_", " ")}</h3>
        {path && (
          <a
            href={vscodeUri(path)}
            className="text-xs text-primary hover:underline"
            target="_blank"
            rel="noreferrer"
          >
            Open in editor
          </a>
        )}
      </div>
      <div className="max-h-[600px] overflow-auto rounded-md border bg-background p-4 text-sm">
        {isMarkdown ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        ) : (
          <pre className="whitespace-pre-wrap text-xs">{content}</pre>
        )}
      </div>
    </div>
  );
}
