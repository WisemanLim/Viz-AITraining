"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ClassicalMLPanel } from "@/components/ClassicalMLPanel";
import { GraphUpload } from "@/components/GraphUpload";
import { HistogramPanel } from "@/components/HistogramPanel";
import { InternalStatePanel } from "@/components/InternalStatePanel";
import { LiveIndicator } from "@/components/LiveIndicator";
import { ProfileTimelinePanel } from "@/components/ProfileTimelinePanel";
import { ScalarChartPanel } from "@/components/ScalarChartPanel";
import { XaiPanel } from "@/components/XaiPanel";
import { useMetricsWebSocket } from "@/hooks/useMetricsWebSocket";
import {
  getRun,
  getProfileTimeline,
  groupScalarsByTag,
  listClassicalCharts,
  listHistograms,
  listInternalMetrics,
  listProfileEvents,
  listRunGraphs,
  listScalars,
  listXaiAttributions,
} from "@/lib/api";
import type {
  ClassicalChart,
  GraphSummary,
  HistogramPoint,
  InternalMetric,
  ProfilePoint,
  ProfileTimelineReport,
  Run,
  ScalarPoint,
  XaiAttribution,
} from "@/lib/types";

const POLL_MS = 4000;

type Tab = "scalars" | "histograms" | "profiling" | "classical" | "internal" | "xai";

export default function RunDetailPage() {
  const params = useParams<{ id: string }>();
  const runId = params.id;

  const [run, setRun] = useState<Run | null>(null);
  const [scalars, setScalars] = useState<ScalarPoint[]>([]);
  const [histograms, setHistograms] = useState<HistogramPoint[]>([]);
  const [profiles, setProfiles] = useState<ProfilePoint[]>([]);
  const [profileTimeline, setProfileTimeline] = useState<ProfileTimelineReport | null>(null);
  const [classicalCharts, setClassicalCharts] = useState<ClassicalChart[]>([]);
  const [internalMetrics, setInternalMetrics] = useState<InternalMetric[]>([]);
  const [xaiItems, setXaiItems] = useState<XaiAttribution[]>([]);
  const [graphs, setGraphs] = useState<GraphSummary[]>([]);
  const [tab, setTab] = useState<Tab>("scalars");
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [liveEnabled, setLiveEnabled] = useState(true);

  const mergeScalars = useCallback((incoming: ScalarPoint[]) => {
    setScalars((prev) => {
      const byKey = new Map(
        prev.map((p) => [`${p.tag}:${p.step}:${p.id}`, p])
      );
      for (const p of incoming) {
        byKey.set(`${p.tag}:${p.step}:${p.id}`, p);
      }
      return [...byKey.values()].sort(
        (a, b) => (a.step ?? 0) - (b.step ?? 0) || a.id - b.id
      );
    });
    setLastUpdated(new Date());
  }, []);

  const wsState = useMetricsWebSocket(runId, mergeScalars, liveEnabled);

  const refresh = useCallback(async () => {
    if (!runId) return;
    try {
      const [
        runData,
        scalarData,
        histData,
        profileData,
        timelineData,
        classicalData,
        internalData,
        xaiData,
        graphData,
      ] = await Promise.all([
        getRun(runId),
        listScalars(runId),
        listHistograms(runId),
        listProfileEvents(runId),
        getProfileTimeline(runId),
        listClassicalCharts(runId),
        listInternalMetrics(runId),
        listXaiAttributions(runId),
        listRunGraphs(runId),
      ]);
      setRun(runData);
      setScalars(scalarData.items);
      setHistograms(histData.items);
      setProfiles(profileData.items);
      setProfileTimeline(timelineData);
      setClassicalCharts(classicalData.items);
      setInternalMetrics(internalData.items);
      setXaiItems(xaiData.items);
      setGraphs(graphData.items);
      setError(null);
      setLastUpdated(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load run");
    }
  }, [runId]);

  useEffect(() => {
    refresh();
    if (!liveEnabled || wsState === "live") return;
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, [refresh, liveEnabled, wsState]);

  const scalarSeries = groupScalarsByTag(scalars);
  const liveLabel =
    wsState === "live"
      ? "WebSocket live"
      : wsState === "connecting"
        ? "Connecting…"
        : "Polling fallback";

  return (
    <div className="space-y-6">
      <div>
        <Link
          href="/"
          className="text-sm text-slate-500 hover:text-cyan-400"
        >
          ← All runs
        </Link>
        <div className="mt-2 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              {run?.name ?? "Loading…"}
            </h1>
            {run && (
              <p className="mt-1 font-mono text-xs text-slate-500">{run.id}</p>
            )}
          </div>
          <div className="flex items-center gap-3">
            <LiveIndicator
              polling={liveEnabled && wsState === "live"}
              lastUpdated={lastUpdated}
              intervalSec={wsState === "live" ? 0 : POLL_MS / 1000}
            />
            <span className="text-xs text-emerald-400/80">{liveLabel}</span>
            <button
              type="button"
              onClick={() => setLiveEnabled((p) => !p)}
              className="rounded-md border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:border-slate-500"
            >
              {liveEnabled ? "Pause live" : "Resume live"}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {run?.params && (
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <h2 className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Hyperparameters
          </h2>
          <pre className="mt-2 overflow-x-auto text-xs text-slate-300">
            {JSON.stringify(run.params, null, 2)}
          </pre>
        </div>
      )}

      <div className="flex gap-2 border-b border-slate-800">
        {(
          [
            "scalars",
            "histograms",
            "profiling",
            "classical",
            "internal",
            "xai",
          ] as const
        ).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`border-b-2 px-4 py-2 text-sm capitalize transition ${
              tab === t
                ? "border-cyan-400 text-cyan-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            {t === "classical"
              ? "classical ML"
              : t === "internal"
                ? "internal state"
                : t}
            <span className="ml-2 rounded bg-slate-800 px-1.5 py-0.5 text-xs">
              {t === "scalars"
                ? scalars.length
                : t === "histograms"
                  ? histograms.length
                  : t === "profiling"
                    ? profiles.length
                    : t === "classical"
                      ? classicalCharts.length
                      : t === "internal"
                        ? internalMetrics.length
                        : xaiItems.length}
            </span>
          </button>
        ))}
      </div>

      {tab === "scalars" ? (
        <ScalarChartPanel series={scalarSeries} />
      ) : tab === "histograms" ? (
        <HistogramPanel histograms={histograms} />
      ) : tab === "profiling" ? (
        <ProfileTimelinePanel events={profiles} timeline={profileTimeline} />
      ) : tab === "classical" ? (
        <ClassicalMLPanel charts={classicalCharts} />
      ) : tab === "internal" ? (
        <InternalStatePanel metrics={internalMetrics} />
      ) : (
        <XaiPanel items={xaiItems} />
      )}

      <section className="space-y-4 border-t border-slate-800 pt-8">
        <h2 className="text-lg font-medium">Model graphs</h2>
        <GraphUpload runId={runId} onUploaded={refresh} />
        {graphs.length > 0 && (
          <ul className="space-y-2 text-sm">
            {graphs.map((g) => (
              <li key={g.id}>
                <Link
                  href={`/graphs/${g.id}`}
                  className="text-cyan-400 hover:text-cyan-300"
                >
                  {g.name}
                </Link>
                <span className="ml-2 text-slate-500">
                  ({g.node_count} ops)
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
