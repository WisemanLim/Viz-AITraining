import RunDetailView from "./view";

// 정적 export(make publish) 지원 — 동적 id 는 클라이언트 useParams 로 처리.
// 빌드 시 플레이스홀더 1건만 생성, 실제 라우팅은 SPA 클라이언트 네비게이션.
// 일반 dev/서버 모드에서는 무시되어 임의 id 가 정상 동작.
export function generateStaticParams() {
  // 데모 번들 run id (frontend/public/demo/data.json) — 정적 export 시 셸 생성.
  return [{ id: "demo" }, { id: "demo-baseline" }];
}

export default function Page() {
  return <RunDetailView />;
}
