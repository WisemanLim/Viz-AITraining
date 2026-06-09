"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ScalarPoint } from "@/lib/types";

const COLORS = ["#22d3ee", "#a78bfa", "#34d399", "#fbbf24", "#f472b6"];

type Props = {
  series: Record<string, ScalarPoint[]>;
};

export function ScalarChartPanel({ series }: Props) {
  const tags = Object.keys(series);
  if (tags.length === 0) {
    return (
      <p className="text-sm text-slate-500">No scalar metrics logged yet.</p>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {tags.map((tag, idx) => {
        const data = [...series[tag]]
          .sort((a, b) => (a.step ?? 0) - (b.step ?? 0))
          .map((p) => ({
            step: p.step ?? 0,
            value: p.value,
          }));
        const color = COLORS[idx % COLORS.length];
        return (
          <div
            key={tag}
            className="rounded-lg border border-slate-800 bg-slate-900/40 p-4"
          >
            <h3 className="mb-3 font-mono text-sm text-slate-300">{tag}</h3>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                  <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                  <XAxis
                    dataKey="step"
                    stroke="#64748b"
                    tick={{ fontSize: 11 }}
                    label={{
                      value: "step",
                      position: "insideBottom",
                      offset: -2,
                      fill: "#64748b",
                      fontSize: 11,
                    }}
                  />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      background: "#0f172a",
                      border: "1px solid #334155",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="value"
                    name={tag}
                    stroke={color}
                    strokeWidth={2}
                    dot={{ r: 3, fill: color }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        );
      })}
    </div>
  );
}
