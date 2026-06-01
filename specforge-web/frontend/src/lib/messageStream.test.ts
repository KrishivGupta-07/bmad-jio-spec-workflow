import { describe, expect, it } from "vitest";
import { mergeStreamItems } from "./messageStream";
import type { Message } from "./api";

describe("mergeStreamItems", () => {
  const messages: Message[] = [
    { id: 1, run_id: 10, role: "assistant", content: "Hello", ts: "2026-01-01T00:00:00" },
    { id: 2, run_id: 10, role: "tool", content: "   ", ts: "2026-01-01T00:00:01" },
  ];

  it("dedupes live WS events that match persisted message ids", () => {
    const items = mergeStreamItems(messages, [
      {
        type: "message",
        id: 1,
        role: "assistant",
        content: "Hello",
        ts: "2026-01-01T00:00:00",
      },
      {
        type: "message",
        id: 3,
        role: "assistant",
        content: "New live only",
        ts: "2026-01-01T00:00:02",
      },
    ]);

    const messageItems = items.filter((i) => i.kind === "message");
    expect(messageItems).toHaveLength(2);
    expect(messageItems.map((i) => i.content)).toEqual(["Hello", "New live only"]);
  });

  it("filters blank persisted messages", () => {
    const items = mergeStreamItems(messages, []);
    expect(items).toHaveLength(1);
    expect(items[0].kind === "message" && items[0].content).toBe("Hello");
  });
});
