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
import type { CompareResult } from "@/lib/types";

const COLORS = ["#22d3ee", "#a78bfa", "#34d399", "#fbbf24", "#f472b6", "#fb7185"];

type Props = {
  data: CompareResult;
};

export function CompareChartPanel({ data }: Props) {
  if (data.tags.length === 0) {
    return <p className="text-sm text-slate-500">No overlapping scalar tags.</p>;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {data.tags.map((tagGroup) => {
        const stepSet = new Set<number>();
        tagGroup.series.forEach((s) =>
          s.points.forEach((p) => stepSet.add(p.step ?? 0))
        );
        const steps = [...stepSet].sort((a, b) => a - b);
        const chartData = steps.map((step) => {
          const row: Record<string, number | string> = { step };
          tagGroup.series.forEach((s) => {
            const pt = s.points.find((p) => (p.step ?? 0) === step);
            if (pt) row[s.run_name] = pt.value;
          });
          return row;
        });

        return (
          <div
            key={tagGroup.tag}
            className="rounded-lg border border-slate-800 bg-slate-900/40 p-4"
          >
            <h3 className="mb-3 font-mono text-sm text-slate-300">
              {tagGroup.tag}
            </h3>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                  <XAxis dataKey="step" stroke="#64748b" tick={{ fontSize: 11 }} />
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
                  {tagGroup.series.map((s, idx) => (
                    <Line
                      key={s.run_id}
                      type="monotone"
                      dataKey={s.run_name}
                      stroke={COLORS[idx % COLORS.length]}
                      strokeWidth={2}
                      dot={{ r: 3 }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        );
      })}
    </div>
  );
}
