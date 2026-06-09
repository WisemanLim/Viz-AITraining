"use client";

import { useMemo, useState } from "react";
import type { ArchitectureView } from "@/lib/types";

const LAYER_GAP = 200;
const NODE_GAP = 52;
const NODE_R = 14;

type Props = {
  arch: ArchitectureView;
};

function nodeColor(hue: string, activation: number, highlight: boolean): string {
  const alpha = highlight ? 0.95 : 0.35 + activation * 0.35;
  if (hue === "input") return `rgba(56, 189, 248, ${alpha})`;
  if (hue === "output") return `rgba(192, 132, 252, ${alpha})`;
  return `rgba(251, 146, 60, ${alpha})`;
}

export function StepForwardViewer({ arch }: Props) {
  const [step, setStep] = useState(0);
  const maxStep = arch.layers.length;

  const positions = useMemo(() => {
    const map = new Map<string, { x: number; y: number }>();
    arch.layers.forEach((layer, li) => {
      const x = 80 + li * LAYER_GAP;
      const totalH = (layer.nodes.length - 1) * NODE_GAP;
      layer.nodes.forEach((node, ni) => {
        map.set(node.id, { x, y: 80 + ni * NODE_GAP - totalH / 2 + 120 });
      });
    });
    return map;
  }, [arch.layers]);

  const width = 80 + arch.layers.length * LAYER_GAP + 80;
  const maxNodes = Math.max(...arch.layers.map((l) => l.nodes.length), 1);
  const height = maxNodes * NODE_GAP + 200;

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-400">
        Step through layers to see activation flow (M5.3 · Conx/nn_vis style).
      </p>
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          disabled={step <= 0}
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          className="rounded border border-slate-600 px-3 py-1.5 text-sm disabled:opacity-40"
        >
          ← Prev
        </button>
        <span className="font-mono text-sm text-cyan-400">
          Layer {step + 1} / {maxStep}: {arch.layers[step]?.name}
        </span>
        <button
          type="button"
          disabled={step >= maxStep - 1}
          onClick={() => setStep((s) => Math.min(maxStep - 1, s + 1))}
          className="rounded border border-slate-600 px-3 py-1.5 text-sm disabled:opacity-40"
        >
          Next →
        </button>
        <button
          type="button"
          onClick={() => setStep(0)}
          className="rounded border border-slate-700 px-3 py-1.5 text-xs text-slate-400"
        >
          Reset
        </button>
      </div>

      <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950/60 p-4">
        <svg width={width} height={height} className="min-w-full">
          <rect width="100%" height="100%" fill="#0f172a" />
          {arch.edges.map((edge) => {
            const s = positions.get(edge.source);
            const t = positions.get(edge.target);
            if (!s || !t) return null;
            const srcLayer = arch.layers.findIndex((l) =>
              l.nodes.some((n) => n.id === edge.source),
            );
            const tgtLayer = arch.layers.findIndex((l) =>
              l.nodes.some((n) => n.id === edge.target),
            );
            const active = srcLayer <= step && tgtLayer <= step;
            return (
              <line
                key={edge.id}
                x1={s.x + NODE_R}
                y1={s.y}
                x2={t.x - NODE_R}
                y2={t.y}
                stroke={active ? "#22d3ee" : "#334155"}
                strokeWidth={active ? 2 : 1}
                opacity={active ? 0.7 : 0.25}
              />
            );
          })}
          {arch.layers.map((layer, li) => (
            <g key={layer.id}>
              <text
                x={positions.get(layer.nodes[0]?.id ?? "")?.x ?? 80 + li * LAYER_GAP}
                y={30}
                fill={li === step ? "#22d3ee" : "#64748b"}
                fontSize={11}
                textAnchor="middle"
                fontWeight={li === step ? 700 : 400}
              >
                {layer.name}
              </text>
              {layer.nodes.map((node) => {
                const p = positions.get(node.id);
                if (!p) return null;
                const highlight = li === step;
                const visited = li < step;
                return (
                  <circle
                    key={node.id}
                    cx={p.x}
                    cy={p.y}
                    r={highlight ? NODE_R + 3 : NODE_R}
                    fill={nodeColor(node.hue, node.activation, highlight || visited)}
                    stroke={highlight ? "#fbbf24" : "#e2e8f0"}
                    strokeWidth={highlight ? 2.5 : 1}
                  />
                );
              })}
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}
