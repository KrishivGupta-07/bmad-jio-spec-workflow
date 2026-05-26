import { useEffect, useRef, useState } from "react";

export type WsEvent = {
  type: string;
  [key: string]: unknown;
};

export function useRunWebSocket(runId: number | null, onEvent?: (event: WsEvent) => void) {
  const [events, setEvents] = useState<WsEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    if (!runId) return;
    setEvents([]);
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}//${host}/api/ws/runs/${runId}`);

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (msg) => {
      try {
        const event = JSON.parse(msg.data) as WsEvent;
        if (event.type === "ping") return;
        setEvents((prev) => [...prev, event]);
        onEventRef.current?.(event);
      } catch {
        /* ignore */
      }
    };

    return () => ws.close();
  }, [runId]);

  return { events, connected };
}
