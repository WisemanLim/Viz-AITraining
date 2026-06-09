"use client";

import type { ArchConnection, ArchitectureView } from "@/lib/types";

const LAYER_GAP = 200;
const NODE_GAP = 52;
const NODE_R = 14;

type Props = {
  arch: ArchitectureView;
};

function nodeColor(hue: string, activation: number): string {
  const alpha = 0.5 + activation * 0.5;
  if (hue === "input") return `rgba(56, 189, 248, ${alpha})`;
  if (hue === "output") return `rgba(192, 132, 252, ${alpha})`;
  return `rgba(251, 146, 60, ${alpha})`;
}

function matrixCellColor(value: number, maxAbs: number): string {
  const t = maxAbs > 0 ? value / maxAbs : 0;
  if (t >= 0) return `rgba(34, 211, 238, ${0.15 + Math.abs(t) * 0.75})`;
  return `rgba(248, 113, 113, ${0.15 + Math.abs(t) * 0.75})`;
}

function WeightMatrixPanel({ conn, fromName, toName }: {
  conn: ArchConnection;
  fromName: string;
  toName: string;
}) {
  const [rows, cols] = conn.shape;
  const flat = conn.matrix.flat();
  const maxAbs = Math.max(...flat.map(Math.abs), 1e-9);
  const cell = Math.min(28, Math.max(14, Math.floor(320 / Math.max(cols, rows))));

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
      <h3 className="text-sm font-medium text-slate-300">
        {fromName} → {toName}{" "}
        <span className="font-mono text-xs text-slate-500">
          [{rows}×{cols}]
        </span>
      </h3>
      <div className="mt-3 overflow-auto">
        <div
          className="inline-grid gap-px font-mono text-[9px] text-slate-400"
          style={{
            gridTemplateColumns: `repeat(${cols}, ${cell}px)`,
          }}
        >
          {conn.matrix.flatMap((row, ri) =>
            row.map((val, ci) => (
              <div
                key={`${ri}-${ci}`}
                title={`W[${ri},${ci}]=${val}`}
                className="flex items-center justify-center rounded-sm border border-slate-800/80"
                style={{
                  width: cell,
                  height: cell,
                  background: matrixCellColor(val, maxAbs),
                }}
              >
                {cols <= 8 && rows <= 8 ? val.toFixed(2) : ""}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export function NeuralArchitectureViewer({ arch }: Props) {
  const positions = new Map<string, { x: number; y: number }>();

  arch.layers.forEach((layer, li) => {
    const x = 80 + li * LAYER_GAP;
    const totalH = (layer.nodes.length - 1) * NODE_GAP;
    layer.nodes.forEach((node, ni) => {
      positions.set(node.id, { x, y: 80 + ni * NODE_GAP - totalH / 2 + 120 });
    });
  });

  const width = 80 + arch.layers.length * LAYER_GAP + 80;
  const maxNodes = Math.max(...arch.layers.map((l) => l.nodes.length), 1);
  const height = maxNodes * NODE_GAP + 200;

  return (
    <div className="space-y-4">
      {arch.artifact_missing && (
        <p className="rounded-md border border-amber-900/40 bg-amber-950/20 px-3 py-2 text-xs text-amber-200/90">
          ONNX artifact가 없어 graph JSON 기반 추정 뷰입니다. 정확한 가중치는
          아래 <strong>Artifact backfill</strong>로 ONNX를 업로드하세요.
        </p>
      )}

      <div className="relative overflow-auto rounded-lg border border-slate-800 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <svg width={width} height={height} className="min-w-full">
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {arch.formulas.map((f) => (
            <text
              key={f.id}
              x={f.x * width}
              y={f.y * height}
              fill="#64748b"
              fontSize={11}
              fontFamily="ui-monospace, monospace"
              opacity={0.7}
            >
              {f.text}
            </text>
          ))}

          {arch.edges.map((edge) => {
            const s = positions.get(edge.source);
            const t = positions.get(edge.target);
            if (!s || !t) return null;
            const mx = (s.x + t.x) / 2;
            const my = (s.y + t.y) / 2;
            const stroke =
              edge.weight >= 0
                ? `rgba(34, 211, 238, ${0.15 + Math.min(Math.abs(edge.weight), 2) * 0.15})`
                : `rgba(248, 113, 113, ${0.15 + Math.min(Math.abs(edge.weight), 2) * 0.15})`;
            return (
              <g key={edge.id}>
                <line
                  x1={s.x + NODE_R}
                  y1={s.y}
                  x2={t.x - NODE_R}
                  y2={t.y}
                  stroke={stroke}
                  strokeWidth={1}
                />
                <text
                  x={mx}
                  y={my - 4}
                  fill="#94a3b8"
                  fontSize={8}
                  textAnchor="middle"
                  fontFamily="ui-monospace, monospace"
                >
                  {edge.label}
                </text>
              </g>
            );
          })}

          {arch.layers.map((layer) => (
            <g key={layer.id}>
              <text
                x={positions.get(layer.nodes[0]?.id ?? "")?.x ?? 0}
                y={30}
                fill="#94a3b8"
                fontSize={11}
                textAnchor="middle"
                fontWeight={600}
              >
                {layer.name}
                <tspan fill="#64748b" fontSize={9}>
                  {" "}
                  ({layer.size})
                </tspan>
              </text>
              {layer.kind === "hidden" && (
                <text
                  x={(positions.get(layer.nodes[0]?.id ?? "")?.x ?? 0) + 60}
                  y={24}
                  fill="#fbbf24"
                  fontSize={9}
                  fontFamily="ui-monospace, monospace"
                >
                  BIAS {layer.bias.label}
                </text>
              )}
              {layer.nodes.map((node) => {
                const p = positions.get(node.id);
                if (!p) return null;
                return (
                  <circle
                    key={node.id}
                    cx={p.x}
                    cy={p.y}
                    r={NODE_R}
                    fill={nodeColor(node.hue, node.activation)}
                    stroke="#e2e8f0"
                    strokeWidth={1.5}
                    filter="url(#glow)"
                  />
                );
              })}
            </g>
          ))}
        </svg>
      </div>

      {arch.connections.length > 0 && (
        <div className="grid gap-4 lg:grid-cols-2">
          {arch.connections.map((conn) => (
            <WeightMatrixPanel
              key={conn.id}
              conn={conn}
              fromName={arch.layers[conn.from_layer]?.name ?? `L${conn.from_layer}`}
              toName={arch.layers[conn.to_layer]?.name ?? `L${conn.to_layer}`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
