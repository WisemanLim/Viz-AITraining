# COMPLIANCE — 교육·에듀테크 (Education / Edtech)

> 자동 생성. 근거: `domains/edtech.yaml` + KSIC 통합표. 규제는 변하므로 references 로 재확인.

## 분류 / Classification

- **KSIC**: P (교육)
- **ISIC/NACE**: P
- **NAICS**: 61

## 한국 규제 (1순위)

| 규제 | 영향 |
|------|------|
| **개인정보보호법(PIPA)** | PII 수명주기(동의·최소·보유·삭제), 과징금 매출 3% |
| **아동·청소년 개인정보(만14세 미만, PIPA §22-2)** | 보호자 동의 게이트 + 본인/보호자 인증, 미성년자 정보 마스킹 |
| **교육 관련 개인정보(학습기록)** | 민감 취급, 벤더 공유 제한, 학습기록 조회 감사로그 |
| **웹접근성(KWCAG)** | 교육콘텐츠 접근성 + a11y CI |

## 국제 기준

- **COPPA** (만13세 미만, 2025-06-23 개정 / 2026-04-22 완전준수, 제3자 공유 전 부모동의)
- **FERPA** (US 학생기록)
- **GDPR** (디지털 동의연령 13~16, DPIA)

## 데이터 등급

| 데이터 | 등급 | 비고 |
|--------|------|------|
| 학습자 PII | 민감 | 이름/연락처/학적 |
| 미성년자 정보 | **규제대상** | 보호자 동의 연동(만14세 미만) — **비-프로덕션(dev/staging/test)에 실데이터 반입 금지** |
| 학습기록/성취도 | 민감 | 교육 민감기록 — Run/metric을 학습기록으로 분류 시 감사로그·retention 적용 |
| 결제(보호자) | **규제대상** | PG — **비-프로덕션에 실데이터 반입 금지** |

## 인프라 패턴

- WebRTC/HLS 실시간 (Phase 2 라이브클래스)
- WebSocket 채팅/퀴즈/실시간 metric
- 버스트 스케일 백엔드(10x 스파이크 — 수업·시험기간)
- Redis 세션 스토어
- SCORM/xAPI/LTI 상호운용 (Phase 2 LMS embed)

## 개발환경 특수 요구

- 비프로드 **미성년자 데이터 마스킹**
- COPPA/PIPA-safe **합성 테스트데이터** (CI에 실제 미성년 PII 금지)
- 보호자 동의 플로우 테스트 픽스처
- **a11y CI 게이트** (KWCAG/WCAG) — Playground UI
- 등록/시험 **버스트 부하 테스트**

## 추가 시험 (test/ 반영)

- [ ] 만14세 미만 가입 시 보호자 동의 없으면 차단
- [ ] 미성년자 PII 비프로드 마스킹 검증
- [ ] 라이브 metric 동시접속 부하 + 지연

## 출처 / References

- https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=659 (만14세미만 보호자동의)
- https://casenote.kr/법령/개인정보_보호법/제22조의2 (PIPA §22-2)
- https://complydog.com/blog/edtech-saas-compliance-student-privacy-gdpr-implementation (COPPA 2025/2026)
- https://www.100ms.live/blog/live-classroom-webrtc-hls
- https://wearebrain.com/blog/best-tech-stack-edtech-2026/
