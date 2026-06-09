"use client";

import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect, useMemo } from "react";
import { layoutGraphNodes, toFlowEdges } from "@/lib/graphLayout";
import type { ModelGraph } from "@/lib/types";

type Props = {
  graph: ModelGraph;
};

export function OnnxGraphViewer({ graph }: Props) {
  const initialNodes = useMemo(
    () => layoutGraphNodes(graph.nodes, graph.edges),
    [graph]
  );
  const initialEdges = useMemo(() => toFlowEdges(graph.edges), [graph]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(layoutGraphNodes(graph.nodes, graph.edges));
    setEdges(toFlowEdges(graph.edges));
  }, [graph, setNodes, setEdges]);

  return (
    <div className="h-[600px] w-full overflow-hidden rounded-lg border border-slate-800 bg-slate-900/50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        minZoom={0.2}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#334155" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(n) =>
            (n.style?.background as string | undefined) ?? "#334155"
          }
          maskColor="rgb(2, 6, 23, 0.8)"
        />
      </ReactFlow>
    </div>
  );
}
