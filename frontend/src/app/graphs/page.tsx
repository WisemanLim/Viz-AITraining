"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { GraphUpload } from "@/components/GraphUpload";
import { listGraphs } from "@/lib/api";
import type { GraphSummary } from "@/lib/types";

export default function GraphsPage() {
  const [graphs, setGraphs] = useState<GraphSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await listGraphs();
      setGraphs(data.items);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load graphs");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Model Graphs
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          ONNX import — Netron-style operation graph (PRD M2.1 / Epic E4)
        </p>
      </div>

      <GraphUpload onUploaded={refresh} />

      {error && (
        <div className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <div>
        <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-slate-500">
          Imported models ({graphs.length})
        </h2>
        {graphs.length === 0 ? (
          <p className="text-sm text-slate-500">No graphs imported yet.</p>
        ) : (
          <div className="overflow-hidden rounded-lg border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Nodes</th>
                  <th className="px-4 py-3">Opset</th>
                  <th className="px-4 py-3">Run</th>
                  <th className="px-4 py-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {graphs.map((g) => (
                  <tr key={g.id} className="hover:bg-slate-900/50">
                    <td className="px-4 py-3">
                      <Link
                        href={`/graphs/${g.id}`}
                        className="font-medium text-cyan-400 hover:text-cyan-300"
                      >
                        {g.name}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-slate-400">{g.node_count}</td>
                    <td className="px-4 py-3 text-slate-400">
                      {g.opset_version ?? "—"}
                    </td>
                    <td className="px-4 py-3">
                      {g.run_id ? (
                        <Link
                          href={`/runs/${g.run_id}`}
                          className="font-mono text-xs text-slate-400 hover:text-cyan-400"
                        >
                          {g.run_id.slice(0, 8)}…
                        </Link>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-400">
                      {new Date(g.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
