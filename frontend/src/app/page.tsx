"use client";

import { useCallback, useEffect, useState } from "react";
import { LiveIndicator } from "@/components/LiveIndicator";
import { RunTable } from "@/components/RunTable";
import { getApiBase, listRuns, seedDemoRun } from "@/lib/api";
import type { Run } from "@/lib/types";

const POLL_MS = 4000;

export default function HomePage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [polling, setPolling] = useState(true);
  const [seeding, setSeeding] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const data = await listRuns();
      setRuns(data.items);
      setConnected(true);
      setError(null);
      setLastUpdated(new Date());
    } catch (e) {
      setConnected(false);
      setError(e instanceof Error ? e.message : "Failed to load runs");
    }
  }, []);

  useEffect(() => {
    refresh();
    if (!polling) return;
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, [refresh, polling]);

  async function onSeedDemo() {
    setSeeding(true);
    try {
      await seedDemoRun();
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create demo run");
    } finally {
      setSeeding(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Experiments</h1>
          <p className="mt-1 text-sm text-slate-400">
            Training runs via dashboard proxy{" "}
            <span className="font-mono text-slate-300">/api → {getApiBase()}</span>
            {connected && (
              <span className="ml-2 text-emerald-500/90">· API OK</span>
            )}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <LiveIndicator
            polling={polling}
            lastUpdated={lastUpdated}
            intervalSec={POLL_MS / 1000}
          />
          <button
            type="button"
            disabled={seeding || !connected}
            onClick={() => void onSeedDemo()}
            className="rounded-md border border-cyan-800 bg-cyan-950/40 px-3 py-1.5 text-xs text-cyan-300 hover:border-cyan-600 disabled:opacity-50"
          >
            {seeding ? "Creating…" : "Create demo run"}
          </button>
          <button
            type="button"
            onClick={() => setPolling((p) => !p)}
            className="rounded-md border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:border-slate-500"
          >
            {polling ? "Pause" : "Resume"}
          </button>
          <button
            type="button"
            onClick={() => refresh()}
            className="rounded-md bg-cyan-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-cyan-500"
          >
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
          {error}
          <p className="mt-1 text-xs text-red-400/80">
            Ensure the API is running: <code>make dev</code>
          </p>
        </div>
      )}

      <RunTable runs={runs} emptyConnected={connected && !error} />
    </div>
  );
}
