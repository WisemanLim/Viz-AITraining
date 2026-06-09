"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Architecture3DViewer } from "@/components/Architecture3DViewer";
import { NeuralArchitectureViewer } from "@/components/NeuralArchitectureViewer";
import { OnnxGraphViewer } from "@/components/OnnxGraphViewer";
import { StepForwardViewer } from "@/components/StepForwardViewer";
import {
  backfillGraphArtifact,
  architectureExportUrl,
  getGraph,
  getGraphArchitecture,
  getGraphArchitecture3d,
} from "@/lib/api";
import type { Architecture3DLayout, ArchitectureView, ModelGraph } from "@/lib/types";

type ViewTab = "architecture" | "3d" | "step" | "operations";

export default function GraphDetailPage() {
  const params = useParams<{ id: string }>();
  const [graph, setGraph] = useState<ModelGraph | null>(null);
  const [arch, setArch] = useState<ArchitectureView | null>(null);
  const [layout3d, setLayout3d] = useState<Architecture3DLayout | null>(null);
  const [tab, setTab] = useState<ViewTab>("architecture");
  const [error, setError] = useState<string | null>(null);
  const [backfillBusy, setBackfillBusy] = useState(false);

  const reload = useCallback(async (id: string) => {
    const [g, a, l3] = await Promise.all([
      getGraph(id),
      getGraphArchitecture(id),
      getGraphArchitecture3d(id),
    ]);
    setGraph(g);
    setArch(a);
    setLayout3d(l3);
    setError(null);
  }, []);

  useEffect(() => {
    if (!params.id) return;
    reload(params.id).catch((e) =>
      setError(e instanceof Error ? e.message : "Failed to load graph")
    );
  }, [params.id, reload]);

  async function onBackfill(file: File) {
    if (!params.id) return;
    setBackfillBusy(true);
    try {
      await backfillGraphArtifact(params.id, file);
      await reload(params.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backfill failed");
    } finally {
      setBackfillBusy(false);
    }
  }

  if (error && !graph) {
    return (
      <div className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
        {error}
      </div>
    );
  }

  if (!graph || !arch || !layout3d) {
    return <p className="text-slate-400">Loading graph…</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <Link href="/graphs" className="text-sm text-slate-500 hover:text-cyan-400">
          ← All graphs
        </Link>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">
          {graph.name}
        </h1>
        <div className="mt-2 flex flex-wrap gap-4 text-xs text-slate-400">
          <span>{graph.metadata.node_count} ops</span>
          <span>{arch.layers.length} layers (MLP view)</span>
          <span>
            source:{" "}
            <span className="font-mono text-slate-300">{arch.source}</span>
          </span>
          <span>opset {graph.metadata.opset_version ?? "—"}</span>
          {graph.run_id && (
            <Link
              href={`/runs/${graph.run_id}`}
              className="text-cyan-500 hover:text-cyan-400"
            >
              linked run →
            </Link>
          )}
        </div>
      </div>

      {arch.artifact_missing && (
        <div className="rounded-lg border border-slate-700 bg-slate-900/40 p-4">
          <p className="text-sm text-slate-300">Artifact backfill</p>
          <p className="mt-1 text-xs text-slate-500">
            Legacy import — upload the original ONNX for full weight matrices.
          </p>
          <label className="mt-3 inline-flex cursor-pointer items-center gap-2 rounded-md border border-slate-600 px-3 py-2 text-sm text-cyan-400 hover:bg-slate-800">
            <input
              type="file"
              accept=".onnx"
              className="hidden"
              disabled={backfillBusy}
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) void onBackfill(f);
                e.target.value = "";
              }}
            />
            {backfillBusy ? "Uploading…" : "Upload ONNX artifact"}
          </label>
        </div>
      )}

      <div className="flex flex-wrap gap-2 border-b border-slate-800">
        {(
          [
            ["architecture", "Neural Network"],
            ["3d", "3D View"],
            ["step", "Step Forward"],
            ["operations", "ONNX Operations"],
          ] as const
        ).map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => setTab(key)}
            className={`border-b-2 px-4 py-2 text-sm transition ${
              tab === key
                ? "border-cyan-400 text-cyan-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            {label}
          </button>
        ))}
        {tab === "architecture" && params.id && (
          <div className="ml-auto flex items-center gap-2 pb-1">
            <a
              href={architectureExportUrl(params.id, "svg")}
              className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-300 hover:border-cyan-500"
            >
              Export SVG
            </a>
            <a
              href={architectureExportUrl(params.id, "png")}
              className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-300 hover:border-cyan-500"
            >
              Export PNG
            </a>
            <a
              href={architectureExportUrl(params.id, "pdf")}
              className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-300 hover:border-cyan-500"
            >
              Export PDF
            </a>
          </div>
        )}
      </div>

      {tab === "architecture" && <NeuralArchitectureViewer arch={arch} />}
      {tab === "3d" && <Architecture3DViewer layout={layout3d} />}
      {tab === "step" && <StepForwardViewer arch={arch} />}
      {tab === "operations" && <OnnxGraphViewer graph={graph} />}

      {error && <p className="text-sm text-red-400">{error}</p>}

      <details className="rounded-lg border border-slate-800 bg-slate-900/30 p-4">
        <summary className="cursor-pointer text-sm text-slate-400">
          Node list ({graph.nodes.length})
        </summary>
        <ul className="mt-3 max-h-48 space-y-1 overflow-y-auto font-mono text-xs text-slate-500">
          {graph.nodes.map((n) => (
            <li key={n.id}>
              {n.op_type}: {n.label}
              {n.shape ? ` — [${n.shape.join(", ")}]` : ""}
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}
