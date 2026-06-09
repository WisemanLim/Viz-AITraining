"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { XaiAttribution } from "@/lib/types";
import { TemporalXaiDashboard } from "@/components/TemporalXaiDashboard";

type Props = {
  items: XaiAttribution[];
};

export function XaiPanel({ items }: Props) {
  if (items.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No XAI attributions yet. Log SHAP/LIME via{" "}
        <code className="text-cyan-500">add_shap_local</code>,{" "}
        <code className="text-cyan-500">add_shap_temporal</code>, or use{" "}
        <code className="text-cyan-500">vizaitrain.xai_adapter</code>.
      </p>
    );
  }

  const temporal = items.filter((i) => i.scope === "temporal");
  const staticItems = items.filter((i) => i.scope !== "temporal");

  return (
    <div className="grid gap-8">
      {temporal.length > 0 && <TemporalXaiDashboard items={temporal} />}
      {staticItems.length > 0 && (
        <div className="grid gap-6">
          {temporal.length > 0 && (
            <h2 className="text-sm font-medium text-slate-400">
              Local / global attributions
            </h2>
          )}
          {staticItems.map((item) => (
            <AttributionBarChart key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}

function AttributionBarChart({ item }: { item: XaiAttribution }) {
  const features = item.data.features as string[];
  const values = item.data.values as number[];
  const rows = features.map((name, i) => ({
    name,
    value: values[i] ?? 0,
  }));

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
      <h3 className="mb-1 text-sm text-slate-300">
        {item.title ?? `${item.method.toUpperCase()} ${item.scope}`}
      </h3>
      {item.data.prediction !== undefined && item.data.prediction !== null && (
        <p className="mb-3 font-mono text-xs text-slate-500">
          prediction = {String(item.data.prediction)}
        </p>
      )}
      {item.data.base_value !== undefined && item.data.base_value !== null && (
        <p className="mb-3 font-mono text-xs text-slate-500">
          base value = {String(item.data.base_value)}
        </p>
      )}
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows} layout="vertical" margin={{ left: 16 }}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
            <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis
              type="category"
              dataKey="name"
              stroke="#64748b"
              width={90}
              tick={{ fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{ background: "#0f172a", border: "1px solid #334155" }}
            />
            <Bar
              dataKey="value"
              fill={item.method === "shap" ? "#22d3ee" : "#a78bfa"}
              radius={[0, 4, 4, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
