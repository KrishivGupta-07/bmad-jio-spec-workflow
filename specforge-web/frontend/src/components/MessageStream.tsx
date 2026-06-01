import { useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import type { Message } from "@/lib/api";
import { mergeStreamItems } from "@/lib/messageStream";
import type { WsEvent } from "@/lib/ws";
import { cn } from "@/lib/utils";

type Props = {
  messages: Message[];
  liveEvents?: WsEvent[];
};

export function MessageStream({ messages, liveEvents = [] }: Props) {
  const parentRef = useRef<HTMLDivElement>(null);

  const items = mergeStreamItems(messages, liveEvents);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 72,
    overscan: 8,
  });

  return (
    <div ref={parentRef} className="h-[420px] overflow-auto rounded-md border bg-muted/20 p-2">
      <div style={{ height: virtualizer.getTotalSize(), position: "relative" }}>
        {virtualizer.getVirtualItems().map((vRow) => {
          const item = items[vRow.index];
          return (
            <div
              key={item.id}
              className="absolute left-0 top-0 w-full px-2 py-1"
              style={{ transform: `translateY(${vRow.start}px)` }}
            >
              {item.kind === "usage" ? (
                <div className="rounded bg-blue-50 px-2 py-1 text-xs text-blue-800">
                  tokens: {String(item.data.prompt_tokens)} / {String(item.data.completion_tokens)} ·
                  ${String(item.data.cost_usd)}
                </div>
              ) : (
                <div className="rounded border bg-background p-2 text-xs">
                  <div className="mb-1 flex items-center gap-2">
                    <span
                      className={cn(
                        "rounded px-1.5 py-0.5 font-medium uppercase",
                        item.role === "assistant" && "bg-primary/10 text-primary",
                        item.role === "user" && "bg-muted",
                        item.role === "tool" && "bg-amber-100 text-amber-900",
                        item.role === "system" && "bg-gray-100",
                      )}
                    >
                      {item.role}
                    </span>
                    {item.ts && (
                      <span className="text-muted-foreground">
                        {new Date(item.ts).toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                  <pre className="whitespace-pre-wrap break-words font-sans">{item.content}</pre>
                </div>
              )}
            </div>
          );
        })}
      </div>
      {items.length === 0 && (
        <p className="p-4 text-center text-sm text-muted-foreground">No messages yet.</p>
      )}
    </div>
  );
}
