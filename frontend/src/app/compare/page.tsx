"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { CompareChartPanel } from "@/components/CompareChartPanel";
import { RunTable } from "@/components/RunTable";
import { compareRuns, listRuns } from "@/lib/api";
import type { CompareResult, Run } from "@/lib/types";

export default function ComparePage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [result, setResult] = useState<CompareResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listRuns()
      .then((d) => setRuns(d.items))
      .catch((e) =>
        setError(e instanceof Error ? e.message : "Failed to load runs")
      );
  }, []);

  const toggle = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else if (next.size < 8) next.add(id);
      return next;
    });
  };

  const runCompare = useCallback(async () => {
    if (selected.size < 2) return;
    try {
      const data = await compareRuns([...selected]);
      setResult(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Compare failed");
    }
  }, [selected]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Compare Runs
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          MLflow-style experiment comparison — overlay metrics, diff hyperparameters (M1.2)
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="overflow-hidden rounded-lg border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
            <tr>
              <th className="px-4 py-3 w-12">Pick</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Params</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {runs.map((run) => (
              <tr key={run.id} className="hover:bg-slate-900/50">
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selected.has(run.id)}
                    onChange={() => toggle(run.id)}
                    className="accent-cyan-500"
                  />
                </td>
                <td className="px-4 py-3">
                  <Link
                    href={`/runs/${run.id}`}
                    className="text-cyan-400 hover:text-cyan-300"
                  >
                    {run.name}
                  </Link>
                </td>
                <td className="px-4 py-3 font-mono text-xs text-slate-500">
                  {run.params ? JSON.stringify(run.params) : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        type="button"
        disabled={selected.size < 2}
        onClick={runCompare}
        className="rounded-md bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-500 disabled:opacity-40"
      >
        Compare {selected.size} runs
      </button>

      {result && (
        <>
          {result.param_diffs.length > 0 && (
            <div className="rounded-lg border border-slate-800 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
                  <tr>
                    <th className="px-4 py-3 text-left">Param</th>
                    {result.runs.map((r) => (
                      <th key={r.id} className="px-4 py-3 text-left">
                        {r.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {result.param_diffs.map((d) => (
                    <tr key={d.key}>
                      <td className="px-4 py-3 font-mono text-cyan-400/80">
                        {d.key}
                      </td>
                      {result.runs.map((r) => (
                        <td key={r.id} className="px-4 py-3 text-slate-400">
                          {JSON.stringify(d.values[r.id] ?? "—")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <CompareChartPanel data={result} />
        </>
      )}

      {runs.length === 0 && !error && (
        <RunTable runs={[]} />
      )}
    </div>
  );
}
