"use client";

import { useEffect, useRef, useState } from "react";
import { getWsBase, IS_STATIC_DEMO } from "@/lib/api";
import type { ScalarPoint } from "@/lib/types";

type WsState = "connecting" | "live" | "polling" | "closed";

export function useMetricsWebSocket(
  runId: string | undefined,
  onScalars: (points: ScalarPoint[]) => void,
  enabled: boolean
) {
  const [state, setState] = useState<WsState>("closed");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // 정적 데모(백엔드 없음) — WS 연결 시도 안 함.
    if (IS_STATIC_DEMO || !runId || !enabled) {
      setState("closed");
      wsRef.current?.close();
      return;
    }

    const base = getWsBase();
    const url = `${base}/api/v1/ws/runs/${runId}/metrics`;
    setState("connecting");

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setState("live");
    ws.onclose = () => setState("polling");
    ws.onerror = () => setState("polling");
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data as string) as {
          type: string;
          metrics?: ScalarPoint[];
        };
        if (msg.type === "scalars" && msg.metrics) {
          onScalars(msg.metrics);
        }
      } catch {
        /* ignore */
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [runId, enabled, onScalars]);

  return state;
}
