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
import type { HistogramPoint } from "@/lib/types";

type Props = {
  histograms: HistogramPoint[];
};

function toBarData(point: HistogramPoint) {
  return point.bin_edges.slice(0, -1).map((edge, i) => ({
    bin: `${edge.toFixed(2)}–${point.bin_edges[i + 1].toFixed(2)}`,
    count: point.counts[i],
  }));
}

export function HistogramPanel({ histograms }: Props) {
  if (histograms.length === 0) {
    return (
      <p className="text-sm text-slate-500">No histogram metrics logged yet.</p>
    );
  }

  const byTag = histograms.reduce<Record<string, HistogramPoint[]>>(
    (acc, h) => {
      if (!acc[h.tag]) acc[h.tag] = [];
      acc[h.tag].push(h);
      return acc;
    },
    {}
  );

  return (
    <div className="grid gap-6">
      {Object.entries(byTag).map(([tag, points]) => {
        const latest = [...points].sort(
          (a, b) => (b.step ?? 0) - (a.step ?? 0)
        )[0];
        const data = toBarData(latest);
        return (
          <div
            key={tag}
            className="rounded-lg border border-slate-800 bg-slate-900/40 p-4"
          >
            <div className="mb-3 flex items-baseline justify-between gap-2">
              <h3 className="font-mono text-sm text-slate-300">{tag}</h3>
              <span className="text-xs text-slate-500">
                step {latest.step ?? "—"} · {points.length} snapshot
                {points.length !== 1 ? "s" : ""}
              </span>
            </div>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data}>
                  <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                  <XAxis
                    dataKey="bin"
                    stroke="#64748b"
                    tick={{ fontSize: 10 }}
                    interval={0}
                    angle={-25}
                    textAnchor="end"
                    height={60}
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
                  <Bar dataKey="count" fill="#22d3ee" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        );
      })}
    </div>
  );
}
