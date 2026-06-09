"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import type { InternalMetric } from "@/lib/types";

type Props = {
  metrics: InternalMetric[];
};

export function InternalStatePanel({ metrics }: Props) {
  if (metrics.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No internal state logged yet. Use SDK{" "}
        <code className="text-cyan-500">add_activation_map</code>,{" "}
        <code className="text-cyan-500">add_gradient_flow</code>, etc.
      </p>
    );
  }

  const byKind = {
    activation_map: metrics.filter((m) => m.kind === "activation_map"),
    gradient_flow: metrics.filter((m) => m.kind === "gradient_flow"),
    embedding: metrics.filter((m) => m.kind === "embedding"),
    hidden_state: metrics.filter((m) => m.kind === "hidden_state"),
  };

  return (
    <div className="grid gap-6">
      {byKind.activation_map.map((m) => (
        <ActivationHeatmap key={m.id} metric={m} />
      ))}
      {byKind.gradient_flow.map((m) => (
        <GradientFlowChart key={m.id} metric={m} />
      ))}
      {byKind.embedding.map((m) => (
        <EmbeddingScatter key={m.id} metric={m} />
      ))}
      {byKind.hidden_state.map((m) => (
        <HiddenStateChart key={m.id} metric={m} />
      ))}
    </div>
  );
}

function ActivationHeatmap({ metric }: { metric: InternalMetric }) {
  const d = metric.data;
  const w = d.width as number;
  const h = d.height as number;
  const values = d.values as number[][];

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
      <h3 className="mb-3 text-sm text-slate-300">
        {metric.title ?? metric.layer ?? "Activation map"}
        <span className="ml-2 font-mono text-xs text-slate-500">
          {w}×{h}
        </span>
      </h3>
      <div
        className="inline-grid gap-px"
        style={{ gridTemplateColumns: `repeat(${w}, 20px)` }}
      >
        {values.flatMap((row, ri) =>
          row.map((v, ci) => (
            <div
              key={`${ri}-${ci}`}
              title={String(v)}
              className="h-5 w-5 rounded-sm"
              style={{
                background: `rgba(34, 211, 238, ${0.1 + v * 0.85})`,
              }}
            />
          )),
        )}
      </div>
    </div>
  );
}

function GradientFlowChart({ metric }: { metric: InternalMetric }) {
  const d = metric.data;
  const timesteps = d.timesteps as number[];
  const layers = d.layers as string[];
  const magnitudes = d.magnitudes as number[][];
  const rows = timesteps.map((t, i) => {
    const row: Record<string, number> = { t };
    layers.forEach((layer, li) => {
      row[layer] = magnitudes[i]?.[li] ?? 0;
    });
    return row;
  });

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
      <h3 className="mb-3 text-sm text-slate-300">
        {metric.title ?? "Gradient flow"}
      </h3>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={rows}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
            <XAxis dataKey="t" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
            <Legend />
            {layers.map((layer, i) => (
              <Line
                key={layer}
                type="monotone"
                dataKey={layer}
                stroke={["#22d3ee", "#a78bfa", "#34d399", "#fbbf24"][i % 4]}
                strokeWidth={2}
                dot={{ r: 2 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function EmbeddingScatter({ metric }: { metric: InternalMetric }) {
  const points = (metric.data.points as { x: number; y: number; label?: string }[]) ?? [];
  const method = (metric.data.method as string) ?? "embedding";

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
      <h3 className="mb-3 text-sm text-slate-300">
        {metric.title ?? `${method} projection`}
      </h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart>
            <CartesianGrid stroke="#1e293b" />
            <XAxis type="number" dataKey="x" stroke="#64748b" />
            <YAxis type="number" dataKey="y" stroke="#64748b" />
            <ZAxis type="category" dataKey="label" />
            <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
            <Scatter data={points} fill="#22d3ee" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function HiddenStateChart({ metric }: { metric: InternalMetric }) {
  const timesteps = metric.data.timesteps as number[];
  const states = metric.data.states as number[][];
  const dimCount = states[0]?.length ?? 0;
  const rows = timesteps.map((t, i) => {
    const row: Record<string, number> = { t };
    for (let d = 0; d < dimCount; d++) {
      row[`d${d}`] = states[i]?.[d] ?? 0;
    }
    return row;
  });

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
      <h3 className="mb-3 text-sm text-slate-300">
        {metric.title ?? "Hidden state trajectory"}
      </h3>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={rows}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
            <XAxis dataKey="t" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
            <Legend />
            {Array.from({ length: dimCount }, (_, d) => (
              <Line
                key={d}
                type="monotone"
                dataKey={`d${d}`}
                name={`dim ${d}`}
                stroke={["#22d3ee", "#f472b6", "#34d399"][d % 3]}
                strokeWidth={2}
                dot={{ r: 2 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
