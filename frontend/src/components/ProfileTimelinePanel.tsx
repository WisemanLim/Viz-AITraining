"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EpochTimeline, ProfilePoint } from "@/lib/types";

type Props = {
  events: ProfilePoint[];
  timeline: { epochs: EpochTimeline[]; total_events: number } | null;
};

export function ProfileTimelinePanel({ events, timeline }: Props) {
  if (events.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No profile events yet. Log via SDK{" "}
        <code className="text-cyan-400">writer.add_profile(...)</code>.
      </p>
    );
  }

  const seriesData = events.map((e, idx) => ({
    idx,
    epoch: e.epoch,
    phase: e.phase,
    cpu: e.cpu_percent,
    gpu: e.gpu_percent,
    throughput: e.throughput,
    duration_ms: e.duration_ms,
  }));

  const bottleneckData =
    timeline?.epochs.map((ep) => ({
      epoch: ep.epoch,
      bottleneck: ep.bottleneck_phase ?? "—",
      phases: ep.phases.length,
    })) ?? [];

  return (
    <div className="space-y-6">
      {timeline && (
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <h3 className="text-sm font-medium text-slate-300">
            Epoch timeline ({timeline.total_events} events)
          </h3>
          <ul className="mt-3 space-y-2 text-xs text-slate-400">
            {timeline.epochs.map((ep) => (
              <li key={ep.epoch} className="rounded border border-slate-800 px-3 py-2">
                <span className="font-mono text-cyan-400">epoch {ep.epoch}</span>
                {" · "}
                bottleneck:{" "}
                <span className="text-amber-400">{ep.bottleneck_phase ?? "—"}</span>
                <div className="mt-1 flex flex-wrap gap-2">
                  {ep.phases.map((p) => (
                    <span
                      key={p.phase}
                      className="rounded bg-slate-800 px-2 py-0.5 font-mono"
                    >
                      {p.phase}: {p.total_duration_ms?.toFixed(0) ?? "—"}ms
                    </span>
                  ))}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <h3 className="mb-3 text-sm text-slate-300">CPU / GPU %</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={seriesData}>
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                <XAxis dataKey="idx" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #334155",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="cpu" name="CPU %" stroke="#22d3ee" dot={false} />
                <Line type="monotone" dataKey="gpu" name="GPU %" stroke="#a78bfa" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <h3 className="mb-3 text-sm text-slate-300">Throughput (samples/s)</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={seriesData}>
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                <XAxis dataKey="idx" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    border: "1px solid #334155",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
                <Bar dataKey="throughput" name="throughput" fill="#34d399" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {bottleneckData.length > 0 && (
        <p className="text-xs text-slate-500">
          Bottleneck phase = longest total duration per epoch (PRD M1.3 acceptance).
        </p>
      )}
    </div>
  );
}
