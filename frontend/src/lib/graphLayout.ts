import type { Edge, Node } from "@xyflow/react";
import type { GraphEdge, GraphNode } from "./types";

const X_GAP = 240;
const Y_GAP = 100;

function opColor(opType: string): string {
  switch (opType) {
    case "Input":
      return "#059669";
    case "Output":
      return "#d97706";
    case "Conv":
    case "ConvTranspose":
      return "#0891b2";
    case "Gemm":
    case "MatMul":
      return "#7c3aed";
    case "Relu":
    case "Sigmoid":
    case "Softmax":
      return "#db2777";
    default:
      return "#334155";
  }
}

function computeLayers(
  nodes: GraphNode[],
  edges: GraphEdge[]
): Map<string, number> {
  const preds = new Map<string, string[]>();
  for (const n of nodes) preds.set(n.id, []);
  for (const e of edges) preds.get(e.target)?.push(e.source);

  const layers = new Map<string, number>();
  const visit = (id: string): number => {
    if (layers.has(id)) return layers.get(id)!;
    const parents = preds.get(id) ?? [];
    const depth =
      parents.length === 0 ? 0 : Math.max(...parents.map(visit)) + 1;
    layers.set(id, depth);
    return depth;
  };
  for (const n of nodes) visit(n.id);
  return layers;
}

export function layoutGraphNodes(
  nodes: GraphNode[],
  edges: GraphEdge[]
): Node[] {
  const layers = computeLayers(nodes, edges);
  const byLayer = new Map<number, GraphNode[]>();

  for (const n of nodes) {
    const layer = layers.get(n.id) ?? 0;
    if (!byLayer.has(layer)) byLayer.set(layer, []);
    byLayer.get(layer)!.push(n);
  }

  const flowNodes: Node[] = [];
  for (const [layer, layerNodes] of [...byLayer.entries()].sort(
    (a, b) => a[0] - b[0]
  )) {
    layerNodes.forEach((n, row) => {
      const shapeStr = n.shape ? `[${n.shape.join(", ")}]` : "";
      flowNodes.push({
        id: n.id,
        position: { x: layer * X_GAP, y: row * Y_GAP },
        data: {
          label: (
            `${n.label}\n${n.op_type}` +
            (shapeStr ? `\n${shapeStr}` : "")
          ).trim(),
        },
        style: {
          background: opColor(n.op_type),
          color: "#f8fafc",
          border: "1px solid #475569",
          borderRadius: 8,
          padding: 8,
          fontSize: 11,
          width: 180,
          whiteSpace: "pre-wrap" as const,
        },
      });
    });
  }
  return flowNodes;
}

export function toFlowEdges(edges: GraphEdge[]): Edge[] {
  return edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.label ?? undefined,
    animated: true,
    style: { stroke: "#64748b" },
    labelStyle: { fill: "#94a3b8", fontSize: 10 },
  }));
}
