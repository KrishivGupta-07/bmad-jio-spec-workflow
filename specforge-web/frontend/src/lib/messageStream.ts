import type { Message } from "@/lib/api";
import type { WsEvent } from "@/lib/ws";

export type StreamItem =
  | { kind: "message"; id: string; role: string; content: string; ts?: string }
  | { kind: "usage"; id: string; data: WsEvent };

/** Merge persisted messages with live WS events, deduping by message id. */
export function mergeStreamItems(messages: Message[], liveEvents: WsEvent[] = []): StreamItem[] {
  const persistedIds = new Set(messages.map((m) => m.id));

  const persisted: StreamItem[] = messages
    .filter((m) => m.content.trim())
    .map((m) => ({
      kind: "message" as const,
      id: `msg-${m.id}`,
      role: m.role,
      content: m.content,
      ts: m.ts,
    }));

  const live: StreamItem[] = [];
  liveEvents.forEach((e, i) => {
    if (e.type === "usage") {
      live.push({ kind: "usage", id: `live-u-${i}`, data: e });
      return;
    }
    if (e.type !== "message") {
      return;
    }
    const msgId = typeof e.id === "number" ? e.id : null;
    if (msgId !== null && persistedIds.has(msgId)) {
      return;
    }
    const content = String(e.content ?? "");
    if (!content.trim()) {
      return;
    }
    live.push({
      kind: "message",
      id: msgId !== null ? `msg-${msgId}` : `live-m-${i}`,
      role: String(e.role ?? "system"),
      content,
      ts: e.ts as string | undefined,
    });
  });

  return [...persisted, ...live];
}
