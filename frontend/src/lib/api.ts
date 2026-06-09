import type {
  ArchitectureView,
  CompareResult,
  GraphList,
  HistogramList,
  ModelGraph,
  ProfileList,
  ProfileTimelineReport,
  ClassicalChartList,
  InternalMetricList,
  Architecture3DLayout,
  XaiAttributionList,
  Run,
  RunList,
  ScalarList,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

// `make publish` 정적 export — 백엔드 없이 번들된 데모 데이터(/demo/data.json)로 동작.
// scripts/publish-pages.sh 가 NEXT_PUBLIC_STATIC_EXPORT=true 를 설정한다.
export const IS_STATIC_DEMO =
  process.env.NEXT_PUBLIC_STATIC_EXPORT === "true";
const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** Browser: same-origin `/api` rewrite (next.config). SSR/build: direct backend URL. */
function requestBase(): string {
  if (typeof window !== "undefined") return "";
  return API_BASE;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${requestBase()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

// ── 정적 데모 번들 ────────────────────────────────────────────────────────────
type DemoBundle = {
  runs: RunList;
  graphs: GraphList;
  runDetail: Record<string, Run>;
  scalars: Record<string, ScalarList>;
  histograms: Record<string, HistogramList>;
  profile: Record<string, ProfileList>;
  profileTimeline: Record<string, ProfileTimelineReport>;
  classical: Record<string, ClassicalChartList>;
  internal: Record<string, InternalMetricList>;
  xai: Record<string, XaiAttributionList>;
  runGraphs: Record<string, GraphList>;
  graphDetail: Record<string, ModelGraph>;
  architecture: Record<string, ArchitectureView>;
  architecture3d: Record<string, Architecture3DLayout>;
  compare: CompareResult;
};

let demoPromise: Promise<DemoBundle> | null = null;
function loadDemo(): Promise<DemoBundle> {
  if (!demoPromise) {
    demoPromise = fetch(`${BASE_PATH}/demo/data.json`, { cache: "force-cache" })
      .then((r) => {
        if (!r.ok) throw new Error(`demo bundle ${r.status}`);
        return r.json() as Promise<DemoBundle>;
      })
      .catch((e) => {
        demoPromise = null;
        throw e;
      });
  }
  return demoPromise;
}

/** id 미존재 시 첫 항목으로 폴백 — 데모 셸 라우트 호환. */
function pick<T>(map: Record<string, T>, id: string): T {
  return map[id] ?? (Object.values(map)[0] as T);
}

function demoUnavailable(action: string): Error {
  return new Error(`데모 모드(정적 배포) — ${action} 은(는) 백엔드가 필요합니다.`);
}

export function getApiBase(): string {
  return IS_STATIC_DEMO ? "demo fixtures (static)" : API_BASE;
}

/** WebSocket must hit the API server directly (Next.js rewrite does not upgrade WS). */
export function getWsBase(): string {
  return API_BASE.replace(/^http/, "ws");
}

export async function listRuns(): Promise<RunList> {
  if (IS_STATIC_DEMO) return (await loadDemo()).runs;
  return apiFetch<RunList>("/api/v1/runs");
}

export async function seedDemoRun(): Promise<{
  run_id: string;
  name: string;
  scalars: number;
  message: string;
}> {
  if (IS_STATIC_DEMO) {
    const b = await loadDemo();
    const r = b.runs.items[0];
    return {
      run_id: r?.id ?? "demo",
      name: r?.name ?? "demo",
      scalars: 0,
      message: "데모 모드 — 번들된 샘플 데이터가 이미 로드돼 있습니다.",
    };
  }
  return apiFetch("/api/v1/demo/seed", { method: "POST" });
}

export async function getRun(runId: string): Promise<Run> {
  if (IS_STATIC_DEMO) return pick((await loadDemo()).runDetail, runId);
  return apiFetch<Run>(`/api/v1/runs/${runId}`);
}

export async function listScalars(runId: string, tag?: string): Promise<ScalarList> {
  if (IS_STATIC_DEMO) {
    const list = pick((await loadDemo()).scalars, runId);
    if (!tag) return list;
    const items = list.items.filter((p) => p.tag === tag);
    return { items, total: items.length };
  }
  const qs = tag ? `?tag=${encodeURIComponent(tag)}` : "";
  return apiFetch<ScalarList>(`/api/v1/runs/${runId}/metrics/scalars${qs}`);
}

export async function listHistograms(
  runId: string,
  tag?: string
): Promise<HistogramList> {
  if (IS_STATIC_DEMO) {
    const list = pick((await loadDemo()).histograms, runId);
    if (!tag) return list;
    const items = list.items.filter((p) => p.tag === tag);
    return { items, total: items.length };
  }
  const qs = tag ? `?tag=${encodeURIComponent(tag)}` : "";
  return apiFetch<HistogramList>(
    `/api/v1/runs/${runId}/metrics/histograms${qs}`
  );
}

export function groupScalarsByTag(
  items: ScalarList["items"]
): Record<string, ScalarList["items"]> {
  return items.reduce<Record<string, ScalarList["items"]>>((acc, point) => {
    if (!acc[point.tag]) acc[point.tag] = [];
    acc[point.tag].push(point);
    return acc;
  }, {});
}

export async function listGraphs(): Promise<GraphList> {
  if (IS_STATIC_DEMO) return (await loadDemo()).graphs;
  return apiFetch<GraphList>("/api/v1/graphs");
}

export async function getGraph(graphId: string): Promise<ModelGraph> {
  if (IS_STATIC_DEMO) return pick((await loadDemo()).graphDetail, graphId);
  return apiFetch<ModelGraph>(`/api/v1/graphs/${graphId}`);
}

export async function listRunGraphs(runId: string): Promise<GraphList> {
  if (IS_STATIC_DEMO) return pick((await loadDemo()).runGraphs, runId);
  return apiFetch<GraphList>(`/api/v1/runs/${runId}/graphs`);
}

export async function uploadOnnxGraph(
  file: File,
  runId?: string
): Promise<ModelGraph> {
  if (IS_STATIC_DEMO) throw demoUnavailable("ONNX 업로드");
  const form = new FormData();
  form.append("file", file);
  if (runId) form.append("run_id", runId);

  const res = await fetch(`${requestBase()}/api/v1/graphs`, {
    method: "POST",
    body: form,
    cache: "no-store",
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  return res.json() as Promise<ModelGraph>;
}

export async function getGraphArchitecture(
  graphId: string
): Promise<ArchitectureView> {
  if (IS_STATIC_DEMO) return pick((await loadDemo()).architecture, graphId);
  return apiFetch<ArchitectureView>(`/api/v1/graphs/${graphId}/architecture`);
}

export async function backfillGraphArtifact(
  graphId: string,
  file: File
): Promise<ModelGraph> {
  if (IS_STATIC_DEMO) throw demoUnavailable("아티팩트 백필");
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${requestBase()}/api/v1/graphs/${graphId}/artifact`, {
    method: "POST",
    body: form,
    cache: "no-store",
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  return res.json() as Promise<ModelGraph>;
}

export async function compareRuns(runIds: string[]): Promise<CompareResult> {
  if (IS_STATIC_DEMO) {
    const cmp = (await loadDemo()).compare;
    const set = new Set(runIds);
    const runs = cmp.runs.filter((r) => set.has(r.id));
    if (runs.length === 0) return cmp; // 폴백: 전체 데모 비교
    return {
      runs,
      param_diffs: cmp.param_diffs,
      tags: cmp.tags.map((t) => ({
        tag: t.tag,
        series: t.series.filter((s) => set.has(s.run_id)),
      })),
    };
  }
  return apiFetch<CompareResult>("/api/v1/compare", {
    method: "POST",
    body: JSON.stringify({ run_ids: runIds }),
  });
}

export async function listProfileEvents(runId: string): Promise<ProfileList> {
  if (IS_STATIC_DEMO) return pick((await loadDemo()).profile, runId);
  return apiFetch<ProfileList>(`/api/v1/runs/${runId}/metrics/profile`);
}

export async function getProfileTimeline(
  runId: string
): Promise<ProfileTimelineReport> {
  if (IS_STATIC_DEMO) return pick((await loadDemo()).profileTimeline, runId);
  return apiFetch<ProfileTimelineReport>(
    `/api/v1/runs/${runId}/metrics/profile/timeline`
  );
}

export async function listClassicalCharts(runId: string): Promise<ClassicalChartList> {
  if (IS_STATIC_DEMO) return pick((await loadDemo()).classical, runId);
  return apiFetch<ClassicalChartList>(`/api/v1/runs/${runId}/metrics/classical`);
}

export async function listInternalMetrics(runId: string): Promise<InternalMetricList> {
  if (IS_STATIC_DEMO) return pick((await loadDemo()).internal, runId);
  return apiFetch<InternalMetricList>(`/api/v1/runs/${runId}/metrics/internal`);
}

export async function listXaiAttributions(runId: string): Promise<XaiAttributionList> {
  if (IS_STATIC_DEMO) return pick((await loadDemo()).xai, runId);
  return apiFetch<XaiAttributionList>(`/api/v1/runs/${runId}/metrics/xai`);
}

export async function getGraphArchitecture3d(
  graphId: string
): Promise<Architecture3DLayout> {
  if (IS_STATIC_DEMO) return pick((await loadDemo()).architecture3d, graphId);
  return apiFetch<Architecture3DLayout>(
    `/api/v1/graphs/${graphId}/architecture/3d`
  );
}

export function architectureExportUrl(
  graphId: string,
  format: "svg" | "png" | "pdf" = "svg"
): string {
  // 정적 데모는 서버 렌더 export 불가 — 빈 문자열로 비활성 신호.
  if (IS_STATIC_DEMO) return "";
  return `/api/v1/graphs/${graphId}/architecture/export?format=${format}`;
}
