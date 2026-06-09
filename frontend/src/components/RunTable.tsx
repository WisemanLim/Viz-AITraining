"use client";

import Link from "next/link";
import type { Run } from "@/lib/types";

type Props = {
  runs: Run[];
  /** API responded successfully but no runs exist yet */
  emptyConnected?: boolean;
};

export function RunTable({ runs, emptyConnected = false }: Props) {
  if (runs.length === 0) {
    return (
      <div
        className={`rounded-lg border p-8 text-center ${
          emptyConnected
            ? "border-slate-700 bg-slate-900/50 text-slate-300"
            : "border-slate-800 bg-slate-900/50 text-slate-400"
        }`}
      >
        {emptyConnected ? (
          <>
            <p className="text-sm font-medium text-emerald-400/90">
              API connected — no experiments yet
            </p>
            <p className="mt-2 text-sm text-slate-400">
              The dashboard is working. Create a run with the button above, or
              log training from Python:
            </p>
          </>
        ) : (
          <p className="text-sm text-slate-400">Loading experiments…</p>
        )}
        <p className="mt-3 text-xs text-slate-500">
          <code className="text-cyan-400">vizaitrain.SummaryWriter</code> · POST{" "}
          <code className="text-cyan-400">/api/v1/runs</code> ·{" "}
          <code className="text-cyan-400">POST /api/v1/demo/seed</code>
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-800">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-900/80 text-xs uppercase tracking-wide text-slate-400">
          <tr>
            <th className="px-4 py-3 font-medium">Name</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3 font-medium">Params</th>
            <th className="px-4 py-3 font-medium">Created</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 bg-slate-950/50">
          {runs.map((run) => (
            <tr key={run.id} className="transition hover:bg-slate-900/60">
              <td className="px-4 py-3">
                <Link
                  href={`/runs/${run.id}`}
                  className="font-medium text-cyan-400 hover:text-cyan-300"
                >
                  {run.name}
                </Link>
                <div className="mt-0.5 font-mono text-xs text-slate-500">
                  {run.id.slice(0, 8)}…
                </div>
              </td>
              <td className="px-4 py-3">
                <span className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
                  {run.status}
                </span>
              </td>
              <td className="max-w-xs truncate px-4 py-3 font-mono text-xs text-slate-400">
                {run.params ? JSON.stringify(run.params) : "—"}
              </td>
              <td className="px-4 py-3 text-slate-400">
                {new Date(run.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
