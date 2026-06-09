export type Run = {
  id: string;
  name: string;
  status: string;
  params: Record<string, unknown> | null;
  created_at: string;
};

export type RunList = {
  items: Run[];
  total: number;
};

export type ScalarPoint = {
  id: number;
  run_id: string;
  tag: string;
  value: number;
  step: number | null;
};

export type ScalarList = {
  items: ScalarPoint[];
  total: number;
};

export type HistogramPoint = {
  id: number;
  run_id: string;
  tag: string;
  step: number | null;
  bin_edges: number[];
  counts: number[];
};

export type HistogramList = {
  items: HistogramPoint[];
  total: number;
};

export type GraphNode = {
  id: string;
  label: string;
  op_type: string;
  inputs: string[];
  outputs: string[];
  shape: (string | number)[] | null;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  label: string | null;
};

export type GraphMetadata = {
  opset_version: number | null;
  producer: string | null;
  node_count: number;
  graph_name: string;
};

export type ModelGraph = {
  id: string;
  run_id: string | null;
  name: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: GraphMetadata;
  created_at: string;
};

export type GraphSummary = {
  id: string;
  run_id: string | null;
  name: string;
  node_count: number;
  opset_version: number | null;
  created_at: string;
};

export type GraphList = {
  items: GraphSummary[];
  total: number;
};

export type ArchNode = {
  id: string;
  index: number;
  activation: number;
  hue: string;
};

export type ArchLayer = {
  id: string;
  name: string;
  kind: string;
  nodes: ArchNode[];
  size: number;
  bias: { value: number; label: string };
};

export type ArchEdge = {
  id: string;
  source: string;
  target: string;
  weight: number;
  label: string;
  source_index: number;
  target_index: number;
};

export type ArchConnection = {
  id: string;
  from_layer: number;
  to_layer: number;
  matrix: number[][];
  shape: number[];
};

export type ArchitectureView = {
  graph_id: string;
  source: "artifact" | "graph_json" | string;
  artifact_missing: boolean;
  layers: ArchLayer[];
  edges: ArchEdge[];
  connections: ArchConnection[];
  formulas: { id: string; text: string; x: number; y: number }[];
};

export type ParamDiff = {
  key: string;
  values: Record<string, unknown>;
};

export type SeriesByRun = {
  run_id: string;
  run_name: string;
  points: ScalarPoint[];
};

export type TagSeries = {
  tag: string;
  series: SeriesByRun[];
};

export type CompareResult = {
  runs: Run[];
  param_diffs: ParamDiff[];
  tags: TagSeries[];
};

export type ProfilePoint = {
  id: number;
  epoch: number;
  phase: string;
  step: number | null;
  cpu_percent: number | null;
  gpu_percent: number | null;
  memory_mb: number | null;
  throughput: number | null;
  duration_ms: number | null;
  recorded_at: string;
};

export type ProfileList = {
  items: ProfilePoint[];
  total: number;
};

export type TimelinePhaseSummary = {
  phase: string;
  avg_cpu_percent: number | null;
  avg_gpu_percent: number | null;
  avg_throughput: number | null;
  total_duration_ms: number | null;
  event_count: number;
};

export type EpochTimeline = {
  epoch: number;
  phases: TimelinePhaseSummary[];
  bottleneck_phase: string | null;
};

export type ProfileTimelineReport = {
  run_id: string;
  epochs: EpochTimeline[];
  total_events: number;
};

export type ClassicalChartType =
  | "learning_curve"
  | "roc"
  | "confusion_matrix"
  | "feature_importance";

export type ClassicalChart = {
  id: number;
  run_id: string;
  chart_type: ClassicalChartType;
  title: string | null;
  data: Record<string, unknown>;
  created_at: string;
};

export type ClassicalChartList = {
  items: ClassicalChart[];
  total: number;
};

export type InternalKind =
  | "activation_map"
  | "gradient_flow"
  | "embedding"
  | "hidden_state";

export type InternalMetric = {
  id: number;
  run_id: string;
  kind: InternalKind;
  layer: string | null;
  step: number | null;
  epoch: number | null;
  title: string | null;
  data: Record<string, unknown>;
  recorded_at: string;
};

export type InternalMetricList = {
  items: InternalMetric[];
  total: number;
};

export type XaiMethod = "shap" | "lime";
export type XaiScope = "local" | "global" | "temporal";

export type XaiAttribution = {
  id: number;
  run_id: string;
  method: XaiMethod;
  scope: XaiScope;
  step: number | null;
  epoch: number | null;
  title: string | null;
  data: Record<string, unknown>;
  recorded_at: string;
};

export type XaiAttributionList = {
  items: XaiAttribution[];
  total: number;
};

export type Architecture3DNode = {
  id: string;
  layer_id: string;
  layer_index: number;
  index: number;
  activation: number;
  hue: string;
  position: [number, number, number];
};

export type Architecture3DLayout = {
  graph_id: string;
  layers: {
    id: string;
    name: string;
    kind: string;
    size: number;
    position: [number, number, number];
  }[];
  nodes: Architecture3DNode[];
  edges: {
    id: string;
    source: string;
    target: string;
    weight: number;
    points: [number, number, number][];
  }[];
  bounds: { x: number; y: number; z: number };
};
