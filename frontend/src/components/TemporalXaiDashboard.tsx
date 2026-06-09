"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { XaiAttribution } from "@/lib/types";

type Props = {
  items: XaiAttribution[];
};

const FEATURE_COLORS = [
  "#22d3ee",
  "#f472b6",
  "#34d399",
  "#fbbf24",
  "#a78bfa",
  "#fb7185",
];

function heatColor(value: number, maxAbs: number): string {
  if (maxAbs <= 0) return "#1e293b";
  const t = Math.min(Math.abs(value) / maxAbs, 1);
  const alpha = 0.25 + t * 0.75;
  if (value >= 0) return `rgba(34, 211, 238, ${alpha})`;
  return `rgba(244, 114, 182, ${alpha})`;
}

export function TemporalXaiDashboard({ items }: Props) {
  if (items.length === 0) return null;

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-cyan-900/40 bg-cyan-950/20 p-4">
        <h2 className="text-sm font-medium text-cyan-300">
          Temporal XAI dashboard (M4.2)
        </h2>
        <p className="mt-1 text-xs text-slate-500">
          Scrub steps, play attribution evolution, compare feature ranks over
          training checkpoints.
        </p>
      </div>
      {items.map((item) => (
        <TemporalXaiCard key={item.id} item={item} />
      ))}
    </div>
  );
}

function TemporalXaiCard({ item }: { item: XaiAttribution }) {
  const steps = item.data.steps as number[];
  const features = item.data.features as string[];
  const overTime = item.data.values_over_time as number[][];

  const [stepIdx, setStepIdx] = useState(0);
  const [playing, setPlaying] = useState(false);

  const maxAbs = useMemo(() => {
    let m = 0;
    for (const row of overTime) {
      for (const v of row) m = Math.max(m, Math.abs(v));
    }
    return m || 1;
  }, [overTime]);

  const rankAtStep = useCallback(
    (idx: number) => {
      const row = overTime[idx] ?? [];
      return features
        .map((f, fi) => ({ f, v: row[fi] ?? 0 }))
        .sort((a, b) => Math.abs(b.v) - Math.abs(a.v))
        .map((x, i) => ({ ...x, rank: i + 1 }));
    },
    [features, overTime],
  );

  const rankDelta = useMemo(() => {
    if (steps.length < 2) return [];
    const first = rankAtStep(0);
    const last = rankAtStep(steps.length - 1);
    const lastMap = new Map(last.map((r) => [r.f, r.rank]));
    return first.map((r) => ({
      feature: r.f,
      from: r.rank,
      to: lastMap.get(r.f) ?? r.rank,
      delta: r.rank - (lastMap.get(r.f) ?? r.rank),
    }));
  }, [rankAtStep, steps.length]);

  const barRows = useMemo(() => {
    const row = overTime[stepIdx] ?? [];
    return features.map((name, i) => ({
      name,
      value: row[i] ?? 0,
    }));
  }, [features, overTime, stepIdx]);

  useEffect(() => {
    if (!playing || steps.length <= 1) return;
    const id = window.setInterval(() => {
      setStepIdx((i) => (i + 1) % steps.length);
    }, 800);
    return () => window.clearInterval(id);
  }, [playing, steps.length]);

  const currentStep = steps[stepIdx] ?? stepIdx;

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm text-slate-200">
            {item.title ?? `${item.method.toUpperCase()} temporal`}
          </h3>
          <p className="font-mono text-xs text-slate-500">
            step {currentStep} · checkpoint {stepIdx + 1}/{steps.length}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setPlaying((p) => !p)}
            className="rounded border border-slate-600 px-3 py-1 text-xs text-cyan-400 hover:border-cyan-500"
          >
            {playing ? "Pause" : "Play"}
          </button>
          <button
            type="button"
            disabled={stepIdx <= 0}
            onClick={() => setStepIdx((i) => Math.max(0, i - 1))}
            className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-300 disabled:opacity-40"
          >
            ←
          </button>
          <button
            type="button"
            disabled={stepIdx >= steps.length - 1}
            onClick={() =>
              setStepIdx((i) => Math.min(steps.length - 1, i + 1))
            }
            className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-300 disabled:opacity-40"
          >
            →
          </button>
        </div>
      </div>

      <input
        type="range"
        min={0}
        max={Math.max(steps.length - 1, 0)}
        value={stepIdx}
        onChange={(e) => {
          setPlaying(false);
          setStepIdx(Number(e.target.value));
        }}
        className="mb-4 w-full accent-cyan-400"
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <div>
          <p className="mb-2 text-xs uppercase tracking-wide text-slate-500">
            Attribution heatmap (feature × step)
          </p>
          <div className="overflow-x-auto rounded border border-slate-800">
            <table className="w-full min-w-[280px] border-collapse text-xs">
              <thead>
                <tr>
                  <th className="border-b border-slate-800 p-2 text-left text-slate-500">
                    feature
                  </th>
                  {steps.map((s) => (
                    <th
                      key={s}
                      className="border-b border-slate-800 p-1 font-mono text-slate-500"
                    >
                      {s}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {features.map((f, fi) => (
                  <tr key={f}>
                    <td className="border-b border-slate-800/50 p-2 text-slate-400">
                      {f}
                    </td>
                    {overTime.map((row, si) => (
                      <td
                        key={`${f}-${steps[si]}`}
                        className="border-b border-slate-800/50 p-0"
                        style={{
                          background: heatColor(row[fi] ?? 0, maxAbs),
                          outline:
                            si === stepIdx
                              ? "2px solid #22d3ee"
                              : undefined,
                        }}
                        title={`${f} @ step ${steps[si]}: ${(row[fi] ?? 0).toFixed(4)}`}
                      >
                        <span className="block px-1 py-2 text-center font-mono text-[10px] text-slate-200">
                          {(row[fi] ?? 0).toFixed(2)}
                        </span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <p className="mb-2 text-xs uppercase tracking-wide text-slate-500">
            Snapshot @ step {currentStep}
          </p>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barRows} layout="vertical" margin={{ left: 8 }}>
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis
                  type="category"
                  dataKey="name"
                  stroke="#64748b"
                  width={72}
                  tick={{ fontSize: 10 }}
                />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #334155",
                  }}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {barRows.map((row, i) => (
                    <Cell
                      key={row.name}
                      fill={
                        row.value >= 0
                          ? FEATURE_COLORS[i % FEATURE_COLORS.length]
                          : "#f472b6"
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {rankDelta.length > 0 && (
        <div className="mt-4 rounded border border-slate-800 bg-slate-950/50 p-3">
          <p className="mb-2 text-xs uppercase tracking-wide text-slate-500">
            Rank change (first → last checkpoint)
          </p>
          <ul className="flex flex-wrap gap-2 text-xs">
            {rankDelta.map((r) => (
              <li
                key={r.feature}
                className="rounded bg-slate-800/80 px-2 py-1 font-mono text-slate-300"
              >
                {r.feature}: #{r.from} → #{r.to}
                {r.delta !== 0 && (
                  <span
                    className={
                      r.delta > 0 ? " text-emerald-400" : " text-amber-400"
                    }
                  >
                    {" "}
                    ({r.delta > 0 ? "+" : ""}
                    {r.delta})
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
